from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
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
from backend.controllers.messages import guardar_mensaje_individual
from backend.models.message import MessageIndidualRequest, MessageIndividualResponse

router = APIRouter()

@router.post("/message/{user_destino}")
def send_individual_message(
    user_destino: int = Path(..., description="ID del usuario destino"),
    data: MessageIndidualRequest = ...
):
    try:
        result = guardar_mensaje_individual(
            id_remitente=data.id_remitente,
            id_receptor=user_destino,
            mensaje=data.mensaje,
            clave_aes_cifrada=data.clave_aes_cifrada,
            firma=data.firma,
            hash_mensaje=data.hash_mensaje
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
