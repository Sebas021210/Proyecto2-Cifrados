from backend.database import Grupos
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from datetime import datetime


def crear_grupo(session: Session, nombre: str, llave_publica: str, tipo_cifrado: str) -> Grupos:
    tipo_cifrado = tipo_cifrado.upper()
    cifrados_validos = ['RSA+AES', 'ECC']

    if tipo_cifrado not in cifrados_validos:
        raise ValueError("Tipo de cifrado no válido. Opciones: RSA+AES o ECC+AES.")

    grupo = Grupos(
        nombre_de_grupo=nombre,
        llave_publica=llave_publica,
        tipo_cifrado=tipo_cifrado
    )

    session.add(grupo)
    try:
        session.commit()
        print("Grupo creado con éxito.")
    except IntegrityError:
        session.rollback()
        raise ValueError("Error: Ya existe un grupo con este nombre o llave.")
    
    return grupo
