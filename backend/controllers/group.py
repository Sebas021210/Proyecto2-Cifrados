from sqlalchemy.exc import IntegrityError
from backend.database import db as db_instance
from backend.database.schemas import MiembrosGrupos, Grupos, User, MensajesGrupo
from backend.controllers.keys import generate_rsa_keys, generate_ecc_keys
from sqlalchemy.orm import Session
from backend.database import db, User, Mensajes, Blockchain
from typing import List, Type
from fastapi import Depends, HTTPException
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os
import json

def agregar_miembro_controller(id_grupo: int, id_usuario: int) -> dict:
    with db_instance.write() as session:
        grupo = session.query(Grupos).filter(Grupos.id_pk == id_grupo).one_or_none()
        if not grupo:
            raise ValueError("El grupo no existe.")

        usuario = session.query(User).filter(User.id_pk == id_usuario).one_or_none()
        if not usuario:
            raise ValueError("El usuario no existe.")

        miembro_existente = session.query(MiembrosGrupos).filter(
            MiembrosGrupos.id_grupo_fk == id_grupo,
            MiembrosGrupos.id_user_fk == id_usuario
        ).first()

        if miembro_existente:
            raise ValueError("El usuario ya es miembro del grupo.")

        nuevo_miembro = MiembrosGrupos(
            id_grupo_fk=id_grupo,
            id_user_fk=id_usuario
        )
        session.add(nuevo_miembro)
        session.flush()  # fuerza que se le asigne id_pk sin cerrar sesión

        # Extrae los datos antes de cerrar la sesión
        return {
            "id_pk": nuevo_miembro.id_pk,
            "id_grupo_fk": nuevo_miembro.id_grupo_fk,
            "id_user_fk": nuevo_miembro.id_user_fk
        }

def crear_grupo(session: Session, nombre: str) -> tuple[Grupos, str]:
    tipo_cifrado = 'ECC'  # Forzado

    # Generar llaves ECC
    llave_privada, llave_publica = generate_ecc_keys()

    grupo = Grupos(
        nombre_de_grupo=nombre,
        tipo_cifrado=tipo_cifrado,
        llave_publica=llave_publica,
    )

    session.add(grupo)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ValueError("Error: Ya existe un grupo con este nombre.")

    return grupo, llave_privada


def listar_grupos(session: Session, user_id: int) -> List[Grupos]:
    """
    Retorna los grupos a los que pertenece el usuario especificado.
    """
    grupos = session.query(Grupos) \
        .join(MiembrosGrupos) \
        .filter(MiembrosGrupos.id_user_fk == user_id) \
        .all()

    return grupos

from sqlalchemy.orm import joinedload

def obtener_detalles_grupo(session: Session, grupo_id: int, user_id: int) -> Grupos:
    grupo = (
        session.query(Grupos)
        .options(joinedload(Grupos.miembros_grupo).joinedload(MiembrosGrupos.usuario))
        .join(MiembrosGrupos)
        .filter(Grupos.id_pk == grupo_id, MiembrosGrupos.id_user_fk == user_id)
        .first()
    )

    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado o acceso denegado")

    return grupo



def listar_usuarios(session: Session) -> list[Type[User]]:
    return session.query(User).all()

def eliminar_miembro_controller(id_grupo: int, id_usuario: int):
    with db_instance.write() as session:
        miembro = session.query(MiembrosGrupos).filter(
            MiembrosGrupos.id_grupo_fk == id_grupo,
            MiembrosGrupos.id_user_fk == id_usuario
        ).first()

        if not miembro:
            raise ValueError("El usuario no es miembro del grupo o ya fue eliminado.")

        session.delete(miembro)



def encrypt_aes_key_with_public_key(aes_key: bytes, public_key_pem: str) -> str:
    """
    Cifra la clave AES con la clave pública del grupo usando ECIES (ECDH + AES-GCM).
    Devuelve un JSON base64 string con:
    {
      "encrypted_key": base64,
      "nonce": base64,
      "ephemeral_public_key": PEM
    }
    """
    peer_public_key = serialization.load_pem_public_key(public_key_pem.encode())

    ephemeral_private_key = ec.generate_private_key(ec.SECP256R1())
    shared_key = ephemeral_private_key.exchange(ec.ECDH(), peer_public_key)

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ecies",
    ).derive(shared_key)

    aesgcm = AESGCM(derived_key)
    nonce = os.urandom(12)
    encrypted_key = aesgcm.encrypt(nonce, aes_key, None)

    ephemeral_public_key = ephemeral_private_key.public_key()
    ephemeral_pem = ephemeral_public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    payload = {
        "encrypted_key": base64.b64encode(encrypted_key).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ephemeral_public_key": ephemeral_pem
    }

    return json.dumps(payload)