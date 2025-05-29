from backend.database import db, User, Mensajes, Blockchain
from backend.controllers.firma import calcular_hash_mensaje, verify_signature, sign_message, encrypt_message_aes, encrypt_aes_key_with_ecc
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os
import hashlib
import base64
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from datetime import datetime

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

        resultado = procesar_mensaje_para_envio(
            mensaje=data.mensaje,
            clave_privada_pem=data.clave_privada_remitente,
            clave_publica_receptor_pem=receptor.public_key,
            algoritmo_hash=algoritmo_hash
        )

        id_bloque = crear_bloque(resultado["hash_mensaje"], session)

        nuevo_mensaje = Mensajes(
            id_remitente=data.id_remitente,
            id_receptor=data.id_receptor,
            mensaje=resultado["mensaje_cifrado"],
            clave_aes_cifrada=resultado["clave_aes_cifrada"],
            firma=resultado["firma"],
            hash_mensaje=resultado["hash_mensaje"],
            id_bloque=id_bloque
        )
        session.add(nuevo_mensaje)
        session.commit()

        return {"message": "Mensaje guardado correctamente", "timestamp": nuevo_mensaje.timestamp}
    
def procesar_mensaje_para_envio(mensaje: str, clave_privada_pem: str, clave_publica_receptor_pem: str, algoritmo_hash="sha256"):
    # Cargar claves
    private_key = load_pem_private_key(clave_privada_pem.encode(), password=None)
    public_key_receptor = load_pem_public_key(clave_publica_receptor_pem.encode())

    # Generar clave AES aleatoria
    clave_aes = os.urandom(32)

    # Cifrar mensaje con AES
    mensaje_cifrado = encrypt_message_aes(mensaje, clave_aes)

    # Cifrar clave AES con ECC (pública del receptor)
    clave_aes_cifrada = encrypt_aes_key_with_ecc(clave_aes, public_key_receptor)

    # Calcular hash
    hash_mensaje = calcular_hash_mensaje(mensaje, algoritmo_hash)

    # Firmar con ECC (clave privada del remitente)
    firma = sign_message(private_key, mensaje)

    return {
        "mensaje_cifrado": mensaje_cifrado,
        "clave_aes_cifrada": clave_aes_cifrada,
        "firma": firma,
        "hash_mensaje": hash_mensaje
    }

def verificar_y_descifrar_mensaje(
    mensaje_cifrado: dict,
    clave_aes_cifrada: dict,
    firma: str,
    hash_mensaje: str,
    clave_privada_receptor_pem: str,
    clave_publica_remitente_pem: str,
    algoritmo_hash: str = "sha256"
) -> str:
    # Derivar clave AES a partir de la clave privada del receptor y la clave pública efímera
    ephemeral_public_key = serialization.load_pem_public_key(clave_aes_cifrada["ephemeral_public_key"].encode())
    receptor_private_key = serialization.load_pem_private_key(clave_privada_receptor_pem.encode(), password=None)
    shared_key = receptor_private_key.exchange(ec.ECDH(), ephemeral_public_key)

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ecies",
    ).derive(shared_key)

    # Descifrar clave AES
    aesgcm = AESGCM(derived_key)
    nonce = base64.b64decode(clave_aes_cifrada["nonce"])
    encrypted_key = base64.b64decode(clave_aes_cifrada["encrypted_key"])
    aes_key = aesgcm.decrypt(nonce, encrypted_key, None)

    # Descifrar mensaje
    aesgcm_mensaje = AESGCM(aes_key)
    nonce_mensaje = base64.b64decode(mensaje_cifrado["nonce"])
    ciphertext = base64.b64decode(mensaje_cifrado["ciphertext"])
    mensaje = aesgcm_mensaje.decrypt(nonce_mensaje, ciphertext, None).decode()

    # Verificar firma
    if not verify_signature(clave_publica_remitente_pem, mensaje, firma):
        raise ValueError("Firma inválida")

    # Verificar hash
    hash_calculado = calcular_hash_mensaje(mensaje, algoritmo_hash)
    if hash_calculado != hash_mensaje:
        raise ValueError("Hash inválido")

    return mensaje
