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

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
from backend.controllers.messages import sign_message, verify_signature

mensajes_router = APIRouter()

class FirmaRequest(BaseModel):
    mensaje: str
    clave_privada: str  # PEM en base64

class VerificarRequest(BaseModel):
    mensaje: str
    clave_publica: str  # PEM en base64
    firma: str  # firma en base64

@mensajes_router.post("/firmar")
def firmar_mensaje(data: FirmaRequest):
    try:
        mensaje_bytes = data.mensaje.encode("utf-8")
        clave_privada_pem = base64.b64decode(data.clave_privada)
        firma = sign_message(clave_privada_pem, mensaje_bytes)
        return {"firma": base64.b64encode(firma).decode()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al firmar: {str(e)}")

@mensajes_router.post("/verificar")
def verificar_mensaje(data: VerificarRequest):
    try:
        mensaje_bytes = data.mensaje.encode("utf-8")
        clave_publica_pem = base64.b64decode(data.clave_publica)
        firma = base64.b64decode(data.firma)
        valido = verify_signature(clave_publica_pem, mensaje_bytes, firma)
        return {"valido": valido}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al verificar: {str(e)}")
