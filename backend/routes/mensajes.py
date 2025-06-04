from fastapi import APIRouter, Depends, HTTPException, Query
from backend.database import db, User, Mensajes, get_db
from backend.controllers.messages import guardar_mensaje_individual
from backend.utils.auth import get_current_user
from backend.controllers.firma import calcular_hash_mensaje, decrypt_message_aes
from backend.models.message import MessageIndividualResponse, MessageReceived, MessageIndividualRequestSimplified
from sqlalchemy.orm import Session
from types import SimpleNamespace as Namespace
from typing import List
import json

router = APIRouter()

# Route to get all messages
@router.get("/all_mensajes")
def get_all_messages():
    with db.read() as session:
        mensajes = session.query(Mensajes).all()
        resultado = []

        for m in mensajes:
            resultado.append({
                "id": m.id,
                "remitente": m.remitente.correo if m.remitente else m.id_remitente,
                "receptor": m.receptor.correo if m.receptor else m.id_receptor,
                "mensaje_cifrado": m.mensaje,
                "firma": m.firma,
                "hash_mensaje": m.hash_mensaje,
                "clave_aes_cifrada": json.loads(m.clave_aes_cifrada),
                "timestamp": m.timestamp.isoformat(),
                "id_bloque": m.id_bloque
            })

        return resultado

# Route to send individual messages
@router.post("/message/{user_destino}")
def send_individual_message(
    user_destino: str,
    message_data: MessageIndividualRequestSimplified,
    algoritmo_hash: str = "sha256",
    db: Session = Depends(get_db),
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
@router.get("/message/received", response_model=List[MessageReceived])
def get_received_messages(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    messages = (
        db.query(Mensajes)
        .filter(Mensajes.id_receptor == user.id_pk)
        .order_by(Mensajes.timestamp.desc())
        .all()
    )

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

# Route to get received messages from a specific user
@router.get("/message/received/{user_remitente}", response_model=List[MessageReceived])
def get_received_messages_from_user(
    user_remitente: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    remitente = db.query(User).filter(User.correo == user_remitente).first()
    if remitente is None:
        raise HTTPException(status_code=404, detail="Usuario remitente no encontrado")

    messages = (
        db.query(Mensajes)
        .filter(Mensajes.id_receptor == user.id_pk, Mensajes.id_remitente == remitente.id_pk)
        .order_by(Mensajes.timestamp.desc())
        .all()
    )

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
def get_sent_messages(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    algoritmo_hash: str = "sha256"
):
    messages = db.query(Mensajes).filter(Mensajes.id_remitente == user.id_pk).order_by(Mensajes.timestamp.desc()).all()
    message_responses = []

    for msg in messages:
        try:
            if msg.clave_aes is None:
                raise ValueError("No se encuentra la clave AES para el remitente")

            mensaje_descifrado = decrypt_message_aes(msg.mensaje, msg.clave_aes)
            hash_recalculado = calcular_hash_mensaje(mensaje_descifrado, algoritmo_hash)
            if hash_recalculado != msg.hash_mensaje:
                raise ValueError("Hash del mensaje no coincide")

        except Exception as e:
            mensaje_descifrado = f"ERROR: {str(e)}"

        message_responses.append(
            MessageReceived(
                id=msg.id,
                message=mensaje_descifrado,
                firma=msg.firma,
                hash_mensaje=msg.hash_mensaje,
                clave_aes=msg.clave_aes,
                clave_aes_cifrada=msg.clave_aes_cifrada,
                timestamp=msg.timestamp,
                remitente=msg.receptor.correo
            )
        )

    return message_responses

# Route to get sent messages to a specific user
@router.get("/message/sent/{user_destino}", response_model=List[MessageReceived])
def get_sent_messages_to_user(
    user_destino: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    algoritmo_hash: str = "sha256"
):
    receptor = db.query(User).filter(User.correo == user_destino).first()
    if receptor is None:
        raise HTTPException(status_code=404, detail="Usuario destino no encontrado")

    messages = (
        db.query(Mensajes)
        .filter(Mensajes.id_remitente == user.id_pk, Mensajes.id_receptor == receptor.id_pk)
        .order_by(Mensajes.timestamp.desc())
        .all()
    )

    message_responses = []
    for msg in messages:
        try:
            if msg.clave_aes is None:
                raise ValueError("No se encuentra la clave AES para el remitente")

            mensaje_descifrado = decrypt_message_aes(msg.mensaje, msg.clave_aes)
            hash_recalculado = calcular_hash_mensaje(mensaje_descifrado, algoritmo_hash)

            if hash_recalculado != msg.hash_mensaje:
                raise ValueError("Hash del mensaje no coincide")

        except Exception as e:
            mensaje_descifrado = f"ERROR: {str(e)}"

        message_responses.append(
            MessageReceived(
                id=msg.id,
                message=mensaje_descifrado,
                firma=msg.firma,
                hash_mensaje=msg.hash_mensaje,
                clave_aes=msg.clave_aes,
                clave_aes_cifrada=msg.clave_aes_cifrada,
                timestamp=msg.timestamp,
                remitente=msg.receptor.correo
            )
        )

    return message_responses
