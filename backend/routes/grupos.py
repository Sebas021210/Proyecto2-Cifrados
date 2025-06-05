from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from backend.models.user import UserBase
from backend.utils.auth import get_current_user
from backend.controllers.keys import cifrar_con_ecdh_aes
from backend.models.message import GrupoCreateRequest, GrupoCreateResponse, MiembroAgregarRequest, MiembroAgregarResponse, GrupoListItem, GrupoDetalleResponse, MiembroDetalle, UserListItem, MiembroEliminarRequest, GroupMessageRequest
from backend.controllers.group import listar_grupos, crear_grupo, agregar_miembro_controller, obtener_detalles_grupo, listar_usuarios, eliminar_miembro_controller, encrypt_aes_key_with_public_key
from backend.database import get_db, User, db, MiembrosGrupos, MensajesGrupo, Grupos
from sqlalchemy.orm import Session
from typing import List
from typing import Annotated
from sqlalchemy import select
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os


router = APIRouter()

'''
Ruta para crear un nuevo grupo. Incluir los ids de los miembros que se quieren agregar al grupo.
'''
@router.post("/newGroup", response_model=GrupoCreateResponse, status_code=201)
async def crear_grupo_endpoint(
    request: GrupoCreateRequest,
    user: UserBase = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    try:
        # Crear grupo y generar llaves
        grupo, llave_privada = crear_grupo(
            session=session,
            nombre=request.nombre,
        )

        # Incluir al creador
        miembros_unicos = set(request.miembros_ids)
        miembros_unicos.add(user.id_pk)

        for miembro_id in miembros_unicos:
            agregar_miembro_controller(
                id_grupo=grupo.id_pk,
                id_usuario=miembro_id
            )

            # Obtener clave pública del usuario
            miembro = session.query(User).filter(User.id_pk == miembro_id).first()
            if not miembro or not miembro.public_key:
                raise HTTPException(status_code=400, detail=f"Usuario {miembro_id} no tiene clave pública válida")

            # Cifrar llave privada del grupo con clave pública del usuario
            try:
                llave_privada_cifrada = cifrar_con_ecdh_aes(
                    priv_key_grupo_pem=llave_privada,
                    pub_key_usuario_pem=miembro.public_key,
                    datos_a_cifrar=llave_privada.encode()
                )

                # Actualizar campo en MiembrosGrupos
                miembro_grupo = session.query(MiembrosGrupos).filter_by(
                    id_grupo_fk=grupo.id_pk,
                    id_user_fk=miembro_id
                ).first()

                miembro_grupo.llave_privada_grupo_cifrada = llave_privada_cifrada
                session.commit()

            except Exception as e:
                session.rollback()
                raise HTTPException(status_code=500, detail=f"Error cifrando llave para usuario {miembro_id}: {str(e)}")

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Error: Ya existe un grupo con este nombre.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando grupo: {str(e)}")

    return GrupoCreateResponse(
        id_pk=grupo.id_pk,
        nombre_de_grupo=grupo.nombre_de_grupo,
        tipo_cifrado=grupo.tipo_cifrado,
        llave_privada=llave_privada,
        mensaje="Grupo creado exitosamente."
    )



@router.post("/miembros", response_model=MiembroAgregarResponse, status_code=201)
async def agregar_miembro(request: MiembroAgregarRequest, user: UserBase = Depends(get_current_user)):
    try:
        miembro_data = agregar_miembro_controller(
            id_grupo=request.id_grupo,
            id_usuario=request.id_usuario,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Error de integridad en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error agregando miembro: {e}")

    return MiembroAgregarResponse(
        id_pk=miembro_data["id_pk"],
        id_grupo_fk=miembro_data["id_grupo_fk"],
        id_user_fk=miembro_data["id_user_fk"],
        mensaje="Miembro agregado exitosamente al grupo."
    )


@router.get("/getGroups", response_model=List[GrupoListItem])
def obtener_grupos(
    session: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    try:
        grupos = listar_grupos(session, current_user.id_pk )
        return grupos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener grupos: {e}")

@router.get("/GroupDetails/{grupo_id}", response_model=GrupoDetalleResponse)
def obtener_grupo(
    grupo_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
):
    grupo = obtener_detalles_grupo(session, grupo_id, user.id_pk)

    miembros = []
    for miembro in grupo.miembros_grupo:
        llave_cifrada = None
        if miembro.llave_privada_grupo_cifrada:
            llave_cifrada = b64encode(miembro.llave_privada_grupo_cifrada).decode()

        miembros.append(
            MiembroDetalle(
                id=miembro.usuario.id_pk,
                nombre=miembro.usuario.nombre,
                correo=miembro.usuario.correo,
                llave_privada_cifrada=llave_cifrada
            )
        )

    return GrupoDetalleResponse(
        id_pk=grupo.id_pk,
        nombre_de_grupo=grupo.nombre_de_grupo,
        tipo_cifrado=grupo.tipo_cifrado,
        miembros=miembros
    )

from fastapi import HTTPException
from base64 import b64encode

@router.get("/GroupMember/{grupo_id}/{user_id}", response_model=MiembroDetalle)
def obtener_miembro_de_grupo(
    grupo_id: int,
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
):
    # Verificar que el usuario que hace la solicitud pertenece al grupo
    grupo = session.query(MiembrosGrupos).filter_by(
        id_grupo_fk=grupo_id,
        id_user_fk=current_user.id_pk
    ).first()

    if not grupo:
        raise HTTPException(status_code=403, detail="No tienes acceso a este grupo.")

    # Obtener miembro solicitado
    miembro = session.query(MiembrosGrupos).filter_by(
        id_grupo_fk=grupo_id,
        id_user_fk=user_id
    ).first()

    if not miembro:
        raise HTTPException(status_code=404, detail="Miembro no encontrado en el grupo.")

    llave_cifrada = None
    if miembro.llave_privada_grupo_cifrada:
        llave_cifrada = b64encode(miembro.llave_privada_grupo_cifrada).decode()

    return MiembroDetalle(
        id=miembro.usuario.id_pk,
        nombre=miembro.usuario.nombre,
        correo=miembro.usuario.correo,
        llave_privada_cifrada=llave_cifrada
    )

@router.get("/usuarios", response_model=List[UserListItem])
def obtener_usuarios(
    session: Session = Depends(get_db),
    usuario_actual: User = Depends(get_current_user)
):
    try:
        usuarios = session.query(User).filter(User.id_pk != usuario_actual.id_pk).all()
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {e}")



@router.delete("/miembros", status_code=200)
async def eliminar_miembro(
    request: MiembroEliminarRequest,
    user: UserBase = Depends(get_current_user)
):
    try:
        eliminar_miembro_controller(
            id_grupo=request.id_grupo,
            id_usuario=request.id_usuario
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando miembro: {e}")

    return {"mensaje": "Miembro eliminado del grupo exitosamente."}


def sign_message(private_key: ec.EllipticCurvePrivateKey, message: str) -> str:
    signature = private_key.sign(message.encode(), ec.ECDSA(hashes.SHA256()))
    return signature.hex()

def encrypt_message_aes(message: str, aes_key: bytes) -> dict:
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(nonce).decode()
    }

@router.post("/group/message/{grupo_id}")
def enviar_mensaje_grupo(
    grupo_id: int,
    datos: GroupMessageRequest,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # 1. Verificar que el usuario es miembro del grupo
    miembro = session.execute(
        select(MiembrosGrupos).where(
            MiembrosGrupos.id_grupo_fk == grupo_id,
            MiembrosGrupos.id_user_fk == user.id_pk
        )
    ).scalar_one_or_none()

    if not miembro:
        raise HTTPException(status_code=403, detail="No eres miembro de este grupo")

    # 2. Obtener clave pública del grupo
    grupo = session.query(Grupos).filter(Grupos.id_pk == grupo_id).first()
    if not grupo or not grupo.llave_publica:
        raise HTTPException(status_code=404, detail="Grupo no encontrado o no tiene clave pública")

    # 3. Cargar clave privada del remitente para firmar
    try:
        private_key = serialization.load_pem_private_key(
            datos.clave_privada_usuario_pem.encode(),
            password=None
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Clave privada inválida o malformateada")

    # 4. Firmar mensaje plano
    firma = sign_message(private_key, datos.mensaje)

    # 5. Generar clave AES y cifrar mensaje
    clave_aes = os.urandom(32)
    cifrado = encrypt_message_aes(datos.mensaje, clave_aes)
    mensaje_cifrado = cifrado["ciphertext"]
    nonce_mensaje = cifrado["nonce"]

    # 6. Cifrar clave AES con clave pública del grupo (ECIES)
    clave_aes_cifrada_json = encrypt_aes_key_with_public_key(clave_aes, grupo.clave_publica_grupo)

    # 7. Calcular hash SHA-256 del mensaje plano para integridad
    hash_mensaje = hashes.Hash(hashes.SHA256())
    hash_mensaje.update(datos.mensaje.encode())
    hash_hex = hash_mensaje.finalize().hex()

    # 8. Guardar mensaje en DB
    nuevo_mensaje = MensajesGrupo(
        id_grupo_fk=grupo_id,
        id_remitente_fk=user.id_pk,
        mensaje=mensaje_cifrado,
        nonce=nonce_mensaje,
        clave_aes_cifrada=clave_aes_cifrada_json,
        firma=firma,
        hash_mensaje=hash_hex,
        timestamp=datetime.utcnow()
    )
    session.add(nuevo_mensaje)
    session.commit()

    return {"msg": "Mensaje grupal enviado correctamente"}