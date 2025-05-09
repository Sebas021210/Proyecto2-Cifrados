from .database import Database
from .schemas import User
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
db = Database(f"{current_directory}/database.db")

__all__ = [
    "db",
    "User",
]