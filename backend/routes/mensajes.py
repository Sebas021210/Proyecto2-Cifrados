from fastapi import APIRouter, Depends, HTTPException
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

@router.post("/message")
def send_message(message_request: MessageIndidualRequest):
    try:
        result = guardar_mensaje_individual(message_request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error saving message: {e}",
        )
