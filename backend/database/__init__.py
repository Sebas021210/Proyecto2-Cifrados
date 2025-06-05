from backend.database.database import Database
from backend.database.schemas import User, Mensajes, Grupos, Blockchain, MensajesGrupo, MiembrosGrupos
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
db = Database(f"{current_directory}/db.sqlite")

__all__ = [
    "db",
    "get_db",
    "User",
    "Blockchain",
    "Mensajes",
    "Grupos",
    "Blockchain",
    "MensajesGrupo",
    "MiembrosGrupos",
]

def get_db():
    """Get the database session."""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()