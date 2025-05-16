from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.models.responses import SuccessfulLoginResponse, SuccessfulRegisterResponse
from backend.models.user import LoginRequest
from backend.database import User, get_db
from backend.utils.auth import create_access_token, verify_password, get_password_hash, get_current_user
from datetime import timedelta

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/login", response_model=SuccessfulLoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.correo == form_data.username).first()
    if not user or not verify_password(form_data.password, user.contraseña):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user.correo}, expires_delta=access_token_expires)
    return SuccessfulLoginResponse(email=user.correo, jwt_token=token)

@router.post("/register", response_model=SuccessfulRegisterResponse)
def register(user: LoginRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.correo == user.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")
    hashed = get_password_hash(user.password)
    new_user = User(correo=user.email, contraseña=hashed)
    db.add(new_user)
    db.commit()
    return SuccessfulRegisterResponse(email=new_user.correo, message="User created successfully")

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.correo}
