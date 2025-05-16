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