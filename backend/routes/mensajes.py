from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from backend.models.responses import SuccessfulLoginResponse, SuccessfulRegisterResponse
from backend.models.user import UserBase, LoginRequest
from backend.database import db, User, Mensajes
from backend.controllers.auth import get_current_user
from backend.controllers.messages import sign_message, verify_signature, generate_ecc_key_pair, calcular_hash_mensaje
from backend.controllers.messages import crear_grupo, agregar_miembro
from backend.controllers.messages import guardar_mensaje_individual
from backend.models.message import FirmaRequest, VerificacionRequest, MensajeSolo
from backend.models.message import GrupoCreateRequest, GrupoCreateResponse, MiembroAgregarRequest, MiembroAgregarResponse
from backend.models.message import MessageIndidualRequest, MessageIndividualResponse, MessageReceived
from types import SimpleNamespace as Namespace

router = APIRouter()

# region: Mensajes y Firmas

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

@router.post("/hash")
def obtener_hash(request: MensajeSolo, algoritmo: str = "sha256"):
    try:
        digest = calcular_hash_mensaje(request.message, algoritmo)
        return {"hash": digest, "algoritmo": algoritmo}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# endregion
# region: Grupos y Miembros

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

# endregion
# region: Mensajes Individuales

# Route to send individual messages
@router.post("/message/{user_destino}")
def send_individual_message(
    user_destino: str,
    message_data: MessageIndidualRequest,
    algoritmo_hash: str = "sha256",
    user: User = Depends(get_current_user),
):
    try:
        receptor = db.query(User).filter(User.correo == user_destino).first()
        if receptor is None:
            raise HTTPException(status_code=404, detail="User not found")

        new_message = guardar_mensaje_individual(
            data=Namespace(
                id_remitente=user.id_pk,
                id_receptor=receptor.id_pk,
                mensaje=message_data.mensaje,
                firma=message_data.firma,
                hash_mensaje=message_data.hash_mensaje,
                clave_aes_cifrada=message_data.clave_aes_cifrada
            ),
            algoritmo_hash=algoritmo_hash
        )

        return MessageIndividualResponse(
            message=new_message["message"],
            timestamp=new_message["timestamp"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Route to get individual messages
@router.get("/message/received", response_model=list[MessageReceived])
def get_received_messages(user: User = Depends(get_current_user)):
    messages = db.query(Mensajes).filter(Mensajes.id_receptor == user.id_pk).order_by(Mensajes.timestamp.desc()).all()
    message_responses = []
    for msg in messages:
        message_responses.append(
            MessageReceived(
                id=msg.id,
                message=msg.mensaje,
                firma=msg.firma,
                hash_mensaje=msg.hash_mensaje,
                clave_aes_cifrada=msg.clave_aes_cifrada,
                timestamp=msg.timestamp,
                remitente=msg.remitente.correo
            )
        )

    return message_responses

# Route to  get individual messages
@router.get("/message/sent", response_model=list[MessageReceived])
def get_sent_messages(user: User = Depends(get_current_user)):
    messages = db.query(Mensajes).filter(Mensajes.id_remitente == user.id_pk).order_by(Mensajes.timestamp.desc()).all()
    message_responses = []
    for msg in messages:
        message_responses.append(
            MessageReceived(
                id=msg.id,
                message=msg.mensaje,
                firma=msg.firma,
                hash_mensaje=msg.hash_mensaje,
                clave_aes_cifrada=msg.clave_aes_cifrada,
                timestamp=msg.timestamp,
                remitente=msg.receptor.correo
            )
        )

    return message_responses

# endregion
