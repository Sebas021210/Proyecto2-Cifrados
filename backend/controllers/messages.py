from backend.database import Grupos
from backend.database.database import db_instance
from sqlalchemy.exc import IntegrityError, NoResultFound
from backend.database.schemas import MiembrosGrupos, Grupos, User

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


def crear_grupo(nombre: str, llave_publica: str, tipo_cifrado: str) -> Grupos:
    tipo_cifrado = tipo_cifrado.upper()
    cifrados_validos = ['RSA+AES', 'ECC']

    if tipo_cifrado not in cifrados_validos:
        raise ValueError("Tipo de cifrado no válido. Opciones: RSA+AES o ECC.")

    with db_instance.write() as session:
        grupo = Grupos(
            nombre_de_grupo=nombre,
            llave_publica=llave_publica,
            tipo_cifrado=tipo_cifrado
        )
        session.add(grupo)
        # session.commit() ya lo hace el context manager db_instance.write()
        return grupo
