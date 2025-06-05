from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import hashlib
import os

from sqlalchemy.orm import Session

from backend.controllers.firma import calcular_hash_mensaje, decrypt_message_aes
from backend.utils.auth import get_current_user
from backend.database import get_db, Blockchain, User, Mensajes, MensajesGrupo
from backend.models.transactions import ManualTransaction

router = APIRouter()


# Obtener historial de blockchain
@router.get("/transactions")
def obtener_historial_blockchain(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    bloques = db.query(Blockchain).order_by(Blockchain.id_bloque_pk).all()

    return [
        {
            "id": b.id_bloque_pk,
            "hash_anterior": b.hash_anterior,
            "hash_actual": b.hash_actual,
            "nonce": b.nonce,
            "timestamp": b.timestamp
        } for b in bloques
    ]


# Crear nueva transacción manualmente
@router.post("/transactions")
def crear_transaccion_manual(
        data: ManualTransaction,
        db: Session = Depends(get_db)
):
    # Obtener último hash
    ultimo_bloque = db.query(Blockchain).order_by(Blockchain.id_bloque_pk.desc()).first()
    hash_anterior = ultimo_bloque.hash_actual if ultimo_bloque else "0" * 64

    # Preparar datos
    nonce = os.urandom(8).hex()
    timestamp = datetime.utcnow()

    contenido = f"{hash_anterior}{data.hash_extra or data.data}{nonce}{timestamp.isoformat()}"
    hash_actual = hashlib.sha256(contenido.encode()).hexdigest()

    nuevo_bloque = Blockchain(
        hash_anterior=str(hash_anterior),
        hash_actual=hash_actual,
        nonce=nonce,
        timestamp=timestamp
    )
    db.add(nuevo_bloque)
    db.commit()

    return {
        "message": "Bloque creado exitosamente",
        "id": nuevo_bloque.id_bloque_pk,
        "hash": hash_actual
    }


@router.get("/transactions/integridad")
def verificar_integridad_blockchain(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    mensajes = db.query(Mensajes).all()
    errores = []

    for i, mensaje in enumerate(mensajes):
        hash = mensaje.hash_mensaje

        blockchain = db.query(Blockchain).filter(Blockchain.id_bloque_pk == mensaje.id_bloque).first()

        if not blockchain:
            errores.append({
                "id": mensaje.id,
                "error": "Bloque asociado no encontrado"
            })
            continue

        # Verificar el hash del mensaje generando el hash esperado
        try:
            mensaje_original = decrypt_message_aes(mensaje.mensaje, mensaje.clave_aes)

            recalculated_hash = calcular_hash_mensaje(
                str(mensaje_original),
                algoritmo="sha256"
            )

            if recalculated_hash != hash:
                errores.append({
                    "id": mensaje.id,
                    "error": "Hash del mensaje no coincide",
                    "esperado": recalculated_hash,
                    "actual": hash
                })

        except Exception as e:
            errores.append({
                "id": mensaje.id,
                "error": f"Error al descifrar el mensaje: {str(e)}"
            })
            continue

        if i == 0:
            expected_hash_anterior = "0" * 64
        else:
            expected_hash_anterior = db.query(Blockchain).filter(Blockchain.id_bloque_pk == mensajes[i - 1].id_bloque).first().hash_actual

        # Validar que el hash_anterior coincide
        if blockchain.hash_anterior != expected_hash_anterior:
            errores.append({
                "id": mensaje.id,
                "error": "Hash anterior no coincide con el hash del bloque anterior"
            })

    if errores:
        return {
            "integridad": False,
            "mensaje": "Existen errores en la cadena de bloques",
            "detalles": errores
        }

    return {
        "integridad": True,
        "mensaje": "Todos los bloques son válidos y la cadena está íntegra"
    }


@router.get("/transactions/integridad-grupal")
def verificar_integridad_blockchain_grupal(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    mensajes = db.query(MensajesGrupo).order_by(MensajesGrupo.id_transacciones_pk).all()
    errores = []

    for i, mensaje in enumerate(mensajes):
        hash_esperado = mensaje.hash_mensaje

        # Obtener bloque correspondiente
        bloque = db.query(Blockchain).filter(Blockchain.id_bloque_pk == mensaje.id_bloque_grupo).first()

        if not bloque:
            errores.append({
                "id": mensaje.id_transacciones_pk,
                "error": "Bloque asociado no encontrado"
            })
            continue

        # # Verificar hash del mensaje
        # try:
        #     recalculated_hash = calcular_hash_mensaje(
        #         mensaje.mensaje,  # Cifrado, asumimos hash sobre texto cifrado (como estaba al enviarlo)
        #         algoritmo="sha256"
        #     )
        #
        #     if recalculated_hash != hash_esperado:
        #         errores.append({
        #             "id": mensaje.id_transacciones_pk,
        #             "error": "Hash del mensaje no coincide",
        #             "esperado": recalculated_hash,
        #             "actual": hash_esperado
        #         })
        #
        # except Exception as e:
        #     errores.append({
        #         "id": mensaje.id_transacciones_pk,
        #         "error": f"Error al calcular hash del mensaje: {str(e)}"
        #     })
        #     continue

        # Verificar el hash anterior
        if i == 0:
            expected_hash_anterior = "0" * 64
        else:
            bloque_anterior = db.query(Blockchain).filter(
                Blockchain.id_bloque_pk == mensajes[i - 1].id_bloque_grupo
            ).first()

            if not bloque_anterior:
                errores.append({
                    "id": mensaje.id_transacciones_pk,
                    "error": "Bloque anterior no encontrado"
                })
                continue

            expected_hash_anterior = bloque_anterior.hash_actual

        if bloque.hash_anterior != expected_hash_anterior:
            errores.append({
                "id": mensaje.id_transacciones_pk,
                "error": "Hash anterior del bloque no coincide con el hash del bloque anterior"
            })

    if errores:
        return {
            "integridad": False,
            "mensaje": "Existen errores en la cadena de bloques de mensajes grupales",
            "detalles": errores
        }

    return {
        "integridad": True,
        "mensaje": "Todos los bloques de mensajes grupales son válidos y la cadena está íntegra"
    }
