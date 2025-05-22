import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from google.auth.transport import requests
from google.oauth2 import id_token

from backend.database import User, get_db
from backend.utils.auth import create_access_token

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


@router.get("/callback")
async def auth_callback(code: str, request: Request, db=Depends(get_db)):
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

    try:
        id_info = id_token.verify_oauth2_token(id_token_value, requests.Request(), GOOGLE_CLIENT_ID)

        email = id_info.get('email')
        name = id_info.get('name')

        # Check if user exists or create one
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(correo=email, nombre=name)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Generate access token
        token = create_access_token(data={"sub": user.email})

        # Return user info + token to frontend
        return JSONResponse(content={
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "name": user.name,
                "email": user.email
            }
        })

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid id_token: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
