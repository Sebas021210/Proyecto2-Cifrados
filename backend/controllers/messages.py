from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
import hashlib

from sqlalchemy.exc import IntegrityError, NoResultFound

from backend.database import Grupos
from backend.database.database import db_instance
from backend.database.schemas import MiembrosGrupos, Grupos, User
from keys import generar_llaves_rsa, generar_llaves_ecc
from sqlalchemy.orm import Session


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
