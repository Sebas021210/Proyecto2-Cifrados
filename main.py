from fastapi import FastAPI, HTTPException
from backend.database.schemas import Usuario, Mensaje, Grupo, Blockchain
from sqlalchemy.orm import Session

# Crear la instancia de FastAPI
app = FastAPI()
