from fastapi import FastAPI, HTTPException
from database import db
from backend.database.schemas import Usuario, Mensaje, Grupo, Blockchain
from sqlalchemy.orm import Session

# Crear la instancia de FastAPI
app = FastAPI()
