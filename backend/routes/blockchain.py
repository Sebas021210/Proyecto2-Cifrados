from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import hashlib
import os

from sqlalchemy.orm import Session

from backend.database import get_db, Blockchain
from backend.models.transactions import ManualTransaction


router = APIRouter(prefix="/blockchain",)


# Obtener historial de blockchain
@router.get("/transactions")
def obtener_historial_blockchain(
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
