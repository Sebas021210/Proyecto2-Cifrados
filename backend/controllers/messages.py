from backend.database import db, User, Mensajes, Blockchain
from backend.controllers.keys import calcular_hash_mensaje, verify_signature
import hashlib
from datetime import datetime
import os

def crear_bloque(hash_mensaje: str, db_session) -> int:
    ultimo_bloque = db_session.query(Blockchain).order_by(Blockchain.id_bloque_pk.desc()).first()
    hash_anterior = ultimo_bloque.hash_actual if ultimo_bloque else "0" * 64
    nonce = os.urandom(8).hex()
    timestamp = datetime.utcnow().isoformat()

    contenido = f"{hash_anterior}{hash_mensaje}{nonce}{timestamp}"
    hash_actual = hashlib.sha256(contenido.encode()).hexdigest()

    nuevo_bloque = Blockchain(
        hash_anterior=hash_anterior,
        hash_actual=hash_actual,
        nonce=nonce,
        timestamp=timestamp
    )
    db_session.add(nuevo_bloque)
    db_session.flush()
    return nuevo_bloque.id_bloque_pk

def guardar_mensaje_individual(data, algoritmo_hash: str = "sha256"):
    with db.write() as session:
        remitente = session.query(User).filter_by(id_pk=data.id_remitente).first()
        receptor = session.query(User).filter_by(id_pk=data.id_receptor).first()

        if not remitente or not receptor:
            raise ValueError("Remitente o receptor no encontrado")

        if algoritmo_hash not in ["sha256", "sha3_256"]:
            raise ValueError("Algoritmo de hash no soportado")

        hash_calculado = calcular_hash_mensaje(data.mensaje, algoritmo_hash)
        if hash_calculado != data.hash_mensaje:
            raise ValueError("El hash del mensaje no coincide, posible alteración.")

        if not verify_signature(remitente.public_key, data.mensaje, data.firma):
            raise ValueError("Firma digital inválida")

        id_bloque = crear_bloque(data.hash_mensaje, session)

        nuevo_mensaje = Mensajes(
            id_remitente=data.id_remitente,
            id_receptor=data.id_receptor,
            mensaje=data.mensaje,
            clave_aes_cifrada=data.clave_aes_cifrada,
            firma=data.firma,
            hash_mensaje=data.hash_mensaje,
            id_bloque=id_bloque
        )
        session.add(nuevo_mensaje)
        session.commit()

        return {"message": "Mensaje guardado correctamente", "timestamp": nuevo_mensaje.timestamp}
    