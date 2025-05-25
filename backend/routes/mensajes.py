from fastapi import APIRouter, Depends, HTTPException, status
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
from backend.controllers.messages import sign_message, verify_signature, generate_ecc_key_pair, hash_sha256, hash_sha3

from backend.controllers.messages import crear_grupo, agregar_miembro
from pydantic import BaseModel, constr

router = APIRouter()

class FirmaRequest(BaseModel):
    private_key: str
    message: str

class VerificacionRequest(BaseModel):
    public_key: str
    message: str
    signature: str

class MensajeSolo(BaseModel):
    message: str


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

@router.post("/hash256")
def obtener_hash_sha256(request: MensajeSolo):
    digest = hash_sha256(request.message)
    return {"hash_sha256": digest}

@router.post("/hash3")
def obtener_hash_sha3(request: MensajeSolo):
    digest = hash_sha3(request.message)
    return {"hash_sha3": digest}


# Pydantic para entrada y salida
class GrupoCreateRequest(BaseModel):
    nombre: str
    llave_publica: str
    tipo_cifrado: str

class GrupoCreateResponse(BaseModel):
    id_pk: int
    nombre_de_grupo: str
    tipo_cifrado: str
    mensaje: str

@router.post("/grupos", response_model=GrupoCreateResponse, status_code=201)
async def crear_grupo(request: GrupoCreateRequest, user: UserBase = Depends(get_current_user)):
    try:
        grupo = crear_grupo(
            nombre=request.nombre,
            llave_publica=request.llave_publica,
            tipo_cifrado=request.tipo_cifrado,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe un grupo con este nombre o llave.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando grupo: {e}")

    return GrupoCreateResponse(
        id_pk=grupo.id_pk,
        nombre_de_grupo=grupo.nombre_de_grupo,
        tipo_cifrado=grupo.tipo_cifrado,
        mensaje="Grupo creado con éxito."
    )

class MiembroAgregarRequest(BaseModel):
    id_grupo: int
    id_usuario: int

class MiembroAgregarResponse(BaseModel):
    id_pk: int
    id_grupo_fk: int
    id_user_fk: int
    mensaje: str

@router.post("/grupos/miembros", response_model=MiembroAgregarResponse, status_code=201)
async def agregar_miembro(request: MiembroAgregarRequest , user: UserBase = Depends(get_current_user)):
    try:
        miembro = agregar_miembro(
            id_grupo=request.id_grupo,
            id_usuario=request.id_usuario,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Error de integridad en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error agregando miembro: {e}")

    return MiembroAgregarResponse(
        id_pk=miembro.id_pk,
        id_grupo_fk=miembro.id_grupo_fk,
        id_user_fk=miembro.id_user_fk,
        mensaje="Miembro agregado exitosamente al grupo."
    )
