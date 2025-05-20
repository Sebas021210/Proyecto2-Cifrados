from backend.database import db, User, Mensajes, Blockchain
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
import hashlib, base64
from datetime import datetime
import os

def calcular_hash_mensaje(mensaje: str, algoritmo: str = "sha256") -> str:
    if algoritmo == "sha256":
        return hashlib.sha256(mensaje.encode()).hexdigest()
    elif algoritmo == "sha3_256":
        return hashlib.sha3_256(mensaje.encode()).hexdigest()
    else:
        raise ValueError("Algoritmo de hash no soportado")

def verificar_firma_ecc(public_key_pem: str, mensaje: str, firma_b64: str) -> bool:
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    firma = base64.b64decode(firma_b64)
    try:
        public_key.verify(
            firma,
            mensaje.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception:
        return False
    
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

def guardar_mensaje_individual(data):
    with db.write() as session:
        remitente = session.query(User).filter_by(id_pk=data.id_remitente).first()
        receptor = session.query(User).filter_by(id_pk=data.id_receptor).first()

        if not remitente or not receptor:
            raise ValueError("Remitente o receptor no encontrado")

        hash_calculado = calcular_hash_mensaje(data.mensaje)
        if hash_calculado != data.hash_mensaje:
            raise ValueError("El hash del mensaje no coincide, posible alteración.")

        if not verificar_firma_ecc(remitente.public_key, data.mensaje, data.firma):
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
    