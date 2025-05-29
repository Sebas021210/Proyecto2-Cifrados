import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Cookie
from fastapi.responses import RedirectResponse, JSONResponse
from google.auth.transport import requests
from google.oauth2 import id_token
from datetime import timedelta
import jwt

from backend.database import User, get_db
from backend.utils.auth import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


@router.get("/login")
async def login(request: Request):
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
        if not user:
            user = User(
                correo=email,
                public_key="public_key",
                hash="hash",
                contraseña="contraseña",
                nombre=name,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(data={"sub": user.correo}, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(data={"sub": user.correo}, expires_delta=timedelta(days=7))

        response = JSONResponse(content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "name": user.nombre,
                "email": user.correo
            }
        })

        print(f"cookie: {refresh_token}")

        # Guardamos el refresh_token en una cookie HttpOnly
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # True en producción con HTTPS
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
            path="/auth/refresh"
        )

        return response

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
