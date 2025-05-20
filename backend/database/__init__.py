from backend.database.database import Database
from backend.database.schemas import User, Mensajes, Grupos, MensajesGrupo, MiembrosGrupos, Blockchain
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
db = Database(f"{current_directory}/db.sqlite")

__all__ = [
    "db",
    "User",
    "Blockchain",
    "Mensajes",
    "Grupos",
    "MiembrosGrupos",
    "MensajesGrupo",
]
