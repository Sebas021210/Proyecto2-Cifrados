from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from backend.models.user import UserBase
from backend.utils.auth import get_current_user
from backend.models.message import GrupoCreateRequest, GrupoCreateResponse, MiembroAgregarRequest, MiembroAgregarResponse, GrupoListItem, GrupoDetalleResponse, MiembroDetalle, UserListItem, MiembroEliminarRequest
from backend.controllers.group import listar_grupos, crear_grupo, agregar_miembro_controller, obtener_detalles_grupo, listar_usuarios, eliminar_miembro_controller
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
        # Crear el grupo y generar llaves
        grupo, llave_privada = crear_grupo(
            session=session,
            nombre=request.nombre,
        )

        # ✅ Agregar al creador como miembro del grupo
        with db.write() as write_session:
            agregar_miembro_controller(
                id_grupo=grupo.id_pk,
                id_usuario=user.id_pk
            )

            # ✅ Agregar los demás miembros, si vienen en el request
            for miembro_id in request.miembros_ids:
                # Evitar agregar dos veces al mismo usuario
                if miembro_id != user.id_pk:
                    try:
                        agregar_miembro_controller(
                            id_grupo=grupo.id_pk,
                            id_usuario=miembro_id
                        )
                    except ValueError as ve:
                        # Si el usuario ya estaba agregado, solo omitir (no levantar error)
                        print(f"Advertencia: {ve}")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando grupo: {e}")

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

    miembros = [
        MiembroDetalle(
            id=miembro.usuario.id_pk,
            nombre=miembro.usuario.nombre,
            correo=miembro.usuario.correo
        )
        for miembro in grupo.miembros_grupo
    ]

    return GrupoDetalleResponse(
        id_pk=grupo.id_pk,
        nombre_de_grupo=grupo.nombre_de_grupo,
        tipo_cifrado=grupo.tipo_cifrado,
        miembros=miembros
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
