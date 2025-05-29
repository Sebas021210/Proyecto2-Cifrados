from fastapi import APIRouter, Depends, HTTPException, Path, Query
from backend.database import db, User, Mensajes
from backend.controllers.messages import guardar_mensaje_individual, verificar_y_descifrar_mensaje
from backend.controllers.auth import get_current_user
from backend.models.message import MessageIndividualResponse, MessageReceived, MessageIndidualRequestSimplified
from types import SimpleNamespace as Namespace

router = APIRouter()

# Route to send individual messages
@router.post("/message/{user_destino}")
def send_individual_message(
    user_destino: str,
    message_data: MessageIndidualRequestSimplified,
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
                clave_privada_remitente=message_data.clave_privada
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
def get_received_messages(
    user: User = Depends(get_current_user),
    clave_privada: str = Query(..., description="Clave privada en formato PEM del receptor"),
    algoritmo_hash: str = "sha256"
):
    messages = db.query(Mensajes).filter(Mensajes.id_receptor == user.id_pk).order_by(Mensajes.timestamp.desc()).all()
    message_responses = []

    for msg in messages:
        try:
            mensaje_descifrado = verificar_y_descifrar_mensaje(
                mensaje_cifrado=msg.mensaje,
                clave_aes_cifrada=msg.clave_aes_cifrada,
                firma=msg.firma,
                hash_mensaje=msg.hash_mensaje,
                clave_privada_receptor_pem=clave_privada,
                clave_publica_remitente_pem=msg.remitente.public_key,
                algoritmo_hash=algoritmo_hash
            )
        except Exception as e:
            mensaje_descifrado = f"ERROR: {str(e)}"

        message_responses.append(
            MessageReceived(
                id=msg.id,
                message=mensaje_descifrado,
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
def get_sent_messages(
    user: User = Depends(get_current_user),
    clave_privada: str = Query(..., description="Clave privada en formato PEM del remitente"),
    algoritmo_hash: str = "sha256"
):
    messages = db.query(Mensajes).filter(Mensajes.id_remitente == user.id_pk).order_by(Mensajes.timestamp.desc()).all()
    message_responses = []

    for msg in messages:
        try:
            mensaje_descifrado = verificar_y_descifrar_mensaje(
                mensaje_cifrado=msg.mensaje,
                clave_aes_cifrada=msg.clave_aes_cifrada,
                firma=msg.firma,
                hash_mensaje=msg.hash_mensaje,
                clave_privada_receptor_pem=clave_privada,
                clave_publica_remitente_pem=user.public_key,
                algoritmo_hash=algoritmo_hash
            )
        except Exception as e:
            mensaje_descifrado = f"ERROR: {str(e)}"

        message_responses.append(
            MessageReceived(
                id=msg.id,
                message=mensaje_descifrado,
                firma=msg.firma,
                hash_mensaje=msg.hash_mensaje,
                clave_aes_cifrada=msg.clave_aes_cifrada,
                timestamp=msg.timestamp,
                remitente=msg.receptor.correo
            )
        )

    return message_responses
