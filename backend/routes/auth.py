import os, io, zipfile
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Cookie
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from google.auth.transport import requests
from google.oauth2 import id_token
from datetime import timedelta
import jwt
from backend.controllers.keys import generate_ecc_keys
from backend.database import User, get_db
from backend.models.responses import SuccessfulRegisterResponse
from backend.models.user import LoginRequest, RegisterRequest
from backend.utils.auth import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM, hash_password, get_current_user
from random import randint
from backend.utils.email_config import send_verification_email  # importa la función
from pydantic import BaseModel, EmailStr
from fastapi import Body
from sqlalchemy.orm import Session


router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

verification_codes = {}  # clave: correo, valor: pin

@router.post("/login")
async def login(login_request: LoginRequest, db=Depends(get_db)):
    """
    Endpoint para iniciar sesión con usuario y contraseña.
    """
    user = db.query(User).filter(User.correo == login_request.email).first()

    if not user or not user.contraseña or user.contraseña != hash_password(login_request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.correo}, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(data={"sub": user.correo}, expires_delta=timedelta(days=7))

    # Guardamos el refresh_token en una cookie HttpOnly
    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "name": user.nombre,
            "email": user.correo
        }
    })

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True en producción con HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/auth/refresh"
    )

    # Retornamos la respuesta de inicio de sesión exitoso
    return response

@router.post("/register")
async def register(register_request: RegisterRequest, db=Depends(get_db)):
    email = register_request.email

    if email in verification_codes:
        raise HTTPException(status_code=400, detail="Verifica tu PIN antes de registrarte.")

    existing_user = db.query(User).filter(User.correo == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    private, public = generate_ecc_keys()

    new_user = User(
        correo=email,
        contraseña=hash_password(register_request.password),
        public_key=public,
        nombre=register_request.name,
        hash=None,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Usuario registrado correctamente",
        "private_key": private,
        "email": email,
    }


@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_callback')
    print(redirect_uri)
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
    )

    return RedirectResponse(url=google_auth_url)

import traceback
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse

@router.get("/callback")
async def auth_callback(code: str, request: Request, db=Depends(get_db)):
    try:
        token_request_uri = "https://oauth2.googleapis.com/token"
        data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': request.url_for('auth_callback'),
            'grant_type': 'authorization_code',
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_request_uri, data=data)
            response.raise_for_status()
            token_response = response.json()

        id_token_value = token_response.get('id_token')
        if not id_token_value:
            raise HTTPException(status_code=400, detail="Missing id_token in response.")

        id_info = id_token.verify_oauth2_token(id_token_value, requests.Request(), GOOGLE_CLIENT_ID)

        email = id_info.get('email')
        name = id_info.get('name')

        user = db.query(User).filter(User.correo == email).first()

        private_key_to_send = None  # Inicializá como None por si no se genera

        if not user:
            private, public = generate_ecc_keys()
            user = User(
                correo=email,
                public_key=public,
                hash=None,
                contraseña=None,
                nombre=name,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            private_key_to_send = private  # Solo si se generó
        else:
            # Si querés permitir que los usuarios existentes que no tienen llave pública se les genere:
            if not user.public_key:
                private, public = generate_ecc_keys()
                user.public_key = public
                db.commit()
                private_key_to_send = private  # Asignar la nueva llave privada

        access_token = create_access_token(data={"sub": user.correo}, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(data={"sub": user.correo}, expires_delta=timedelta(days=7))

        frontend_callback_url = "http://localhost:5173/auth/callback"

        # Agregar solo si existe
        query_data = {
            "access_token": access_token,
            "name": user.nombre,
            "email": user.correo,
        }

        if private_key_to_send:
            query_data["private_key"] = private_key_to_send

        query_params = urlencode(query_data)
        redirect_url = f"{frontend_callback_url}?{query_params}"

        redirect_response = RedirectResponse(url=redirect_url)

        redirect_response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
            path="/auth/refresh"
        )

        return redirect_response

    except Exception as e:
        print("❌ Error en /callback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/refresh")
async def refresh_token(refresh_token: str = Cookie(None), db = Depends(get_db)):
    print(f"Refresh token received: {refresh_token}")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.correo == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = create_access_token(data={"sub": user.correo})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid refresh token. Error: {str(e)}")

@router.post("/verify-pin")
async def verify_pin(email: EmailStr = Body(...), pin: str = Body(...)):
    expected_pin = verification_codes.get(email)
    if not expected_pin:
        raise HTTPException(status_code=400, detail="No se encontró PIN para este correo.")
    if pin != expected_pin:
        raise HTTPException(status_code=400, detail="PIN incorrecto")

    del verification_codes[email]  # eliminar después de verificar

    return {"message": "Correo verificado exitosamente ✅"}

@router.get("/test")
async def test_auth(user = Depends(get_current_user)):
    """
    Endpoint de prueba para verificar la autenticación.
    """
    return {"message": "Autenticación exitosa", "user": {"email": user.correo, "name": user.nombre}}


class EmailRequest(BaseModel):
    email: EmailStr

@router.post("/send-pin")
async def send_pin(request: EmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.correo == request.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Este correo ya está registrado.")

    pin = str(randint(100000, 999999))
    verification_codes[request.email] = pin

    await send_verification_email(request.email, pin)

    return {"message": "PIN enviado al correo correctamente."}