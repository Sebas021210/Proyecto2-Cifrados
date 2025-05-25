from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
import hashlib

from sqlalchemy.exc import IntegrityError, NoResultFound

from backend.database import Grupos
from backend.database.database import db_instance
from backend.database.schemas import MiembrosGrupos, Grupos, User
from keys import generar_llaves_rsa, generar_llaves_ecc
from sqlalchemy.orm import Session

from backend.database import db, User, Mensajes, Blockchain
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
import hashlib, base64
from datetime import datetime
import os


def sign_message(private_key_pem: str, message: str) -> str:
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    signature = private_key.sign(message.encode(), ec.ECDSA(hashes.SHA256()))
    return signature.hex()

def verify_signature(public_key_pem: str, message: str, signature_hex: str) -> bool:
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    signature = bytes.fromhex(signature_hex)
    try:
        public_key.verify(signature, message.encode(), ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False

def generate_ecc_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ).decode()

    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return {
        "private_key": private_pem,
        "public_key": public_pem
    }


def hash_sha256(message: str) -> str:
    digest = hashlib.sha256(message.encode()).hexdigest()
    return digest

def hash_sha3(message: str) -> str:
    digest = hashlib.sha3_256(message.encode()).hexdigest()
    return digest

def agregar_miembro(id_grupo: int, id_usuario: int) -> MiembrosGrupos:
    with db_instance.write() as session:
        # Verificar que el grupo existe
        grupo = session.query(Grupos).filter(Grupos.id_pk == id_grupo).one_or_none()
        if not grupo:
            raise ValueError("El grupo no existe.")

        # Verificar que el usuario existe
        usuario = session.query(User).filter(User.id_pk == id_usuario).one_or_none()
        if not usuario:
            raise ValueError("El usuario no existe.")

        # Verificar si ya es miembro
        miembro_existente = session.query(MiembrosGrupos).filter(
            MiembrosGrupos.id_grupo_fk == id_grupo,
            MiembrosGrupos.id_user_fk == id_usuario
        ).first()

        if miembro_existente:
            raise ValueError("El usuario ya es miembro del grupo.")

        # Crear miembro
        nuevo_miembro = MiembrosGrupos(
            id_grupo_fk=id_grupo,
            id_user_fk=id_usuario
        )
        session.add(nuevo_miembro)
        return nuevo_miembro


def crear_grupo(session: Session, nombre: str, tipo_cifrado: str) -> Grupos:
    tipo_cifrado = tipo_cifrado.upper()
    cifrados_validos = ['RSA+AES', 'ECC']
    
    if tipo_cifrado not in cifrados_validos:
        raise ValueError("Tipo de cifrado no válido. Opciones: RSA+AES o ECC.")
    
    # Generar llaves
    if tipo_cifrado == 'RSA+AES':
        llave_privada, llave_publica = generar_llaves_rsa()
    elif tipo_cifrado == 'ECC':
        llave_privada, llave_publica = generar_llaves_ecc()
    
    grupo = Grupos(
        nombre_de_grupo=nombre,
        tipo_cifrado=tipo_cifrado,
        llave_publica=llave_publica,
        # Opcional: puedes guardar la privada cifrada si lo deseas
    )

    session.add(grupo)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ValueError("Error: Ya existe un grupo con este nombre.")

    return grupo

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
    
