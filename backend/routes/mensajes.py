from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from backend.models.responses import SuccessfulLoginResponse, SuccessfulRegisterResponse
from backend.models.user import UserBase, LoginRequest
from backend.database import db, User
from backend.controllers.auth import (
    login as login_controller,
    register as register_controller,
    get_current_user,
)
from backend.controllers.keys import generate_rsa_keys, generate_ecc_keys

from pydantic import BaseModel
from backend.controllers.messages import sign_message, verify_signature, generate_ecc_key_pair

router = APIRouter()

class FirmaRequest(BaseModel):
    private_key: str
    message: str

class VerificacionRequest(BaseModel):
    public_key: str
    message: str
    signature: str

@router.post("/firmar")
def firmar(request: FirmaRequest):
    signature = sign_message(request.private_key, request.message)
    return {"firma": signature}

@router.post("/verificar")
def verificar(request: VerificacionRequest):
    is_valid = verify_signature(request.public_key, request.message, request.signature)
    return {"valida": is_valid}

@router.get("/generar-claves-ecc")
def generar_claves_ecc():
    return generate_ecc_key_pair()
