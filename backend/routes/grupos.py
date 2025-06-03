from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from backend.models.user import UserBase
from backend.utils.auth import get_current_user
from backend.models.message import GrupoCreateRequest, GrupoCreateResponse, MiembroAgregarRequest, MiembroAgregarResponse, GrupoListItem, GrupoDetalleResponse, InvitarUsuarioRequest, UserListItem
from backend.controllers.group import listar_grupos, crear_grupo, agregar_miembro_controller, obtener_detalles_grupo, invitar_usuario_a_grupo, listar_usuarios
from backend.database import get_db, User, db
from sqlalchemy.orm import Session
from typing import List
from typing import Annotated

router = APIRouter()

@router.post("/newGroup", response_model=GrupoCreateResponse, status_code=201)
async def crear_grupo_endpoint(
    request: GrupoCreateRequest,
    user: UserBase = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    try:
        grupo, llave_privada = crear_grupo(
            session=session,
            nombre=request.nombre,
        )

        # ✅ Agregar automáticamente al creador como miembro del grupo
        with db.write() as write_session:
            agregar_miembro_controller(
                id_grupo=grupo.id_pk,
                id_usuario=user.id_pk,
            )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Ya existe un grupo con este nombre.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando grupo: {e}")

    return GrupoCreateResponse(
        id_pk=grupo.id_pk,
        nombre_de_grupo=grupo.nombre_de_grupo,
        tipo_cifrado=grupo.tipo_cifrado,
        llave_privada=llave_privada,
        mensaje="Grupo creado con éxito y te agregaste como miembro."
    )


@router.post("/miembros", response_model=MiembroAgregarResponse, status_code=201)
async def agregar_miembro(request: MiembroAgregarRequest , user: UserBase = Depends(get_current_user)):
    try:
        miembro = agregar_miembro_controller(
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
        id_pk=miembro.id_pk,
        id_grupo_fk=miembro.id_grupo_fk,
        id_user_fk=miembro.id_user_fk,
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

    miembros = [
        miembro.id_user_fk for miembro in grupo.miembros_grupo
    ]

    return GrupoDetalleResponse(
        id_pk=grupo.id_pk,
        nombre_de_grupo=grupo.nombre_de_grupo,
        tipo_cifrado=grupo.tipo_cifrado,
        miembros=miembros
    )

@router.post("/invite/{grupo_id}", status_code=200)
def invitar_usuario(
    grupo_id: int,
    body: InvitarUsuarioRequest,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_db)]
):
    invitar_usuario_a_grupo(
        session=session,
        id_grupo=grupo_id,
        id_usuario_invitado=body.id_usuario,
        id_usuario_que_invita=user.id_pk
    )
    return {"mensaje": "Usuario invitado correctamente al grupo."}

outer = APIRouter()

@router.get("/usuarios", response_model=List[UserListItem])
def obtener_usuarios(session: Session = Depends(get_db)):
    try:
        usuarios = listar_usuarios(session)
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {e}")

