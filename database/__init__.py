from backend.database.database import Database
from backend.database.schemas import Usuario, Mensaje, Grupo, Blockchain
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
db = Database(f"{current_directory}/db.sqlite")

__all__ = [
    "db",
    "Usuario",
    "Mensaje",
    "Grupo",
    "Blockchain",
]
