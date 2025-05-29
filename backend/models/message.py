from pydantic import BaseModel
from datetime import datetime

class FirmaRequest(BaseModel):
    private_key: str
    message: str

class VerificacionRequest(BaseModel):
    public_key: str
    message: str
    signature: str

class MensajeSolo(BaseModel):
    message: str

class GrupoCreateRequest(BaseModel):
    nombre: str
    llave_publica: str
    tipo_cifrado: str

class GrupoCreateResponse(BaseModel):
    id_pk: int
    nombre_de_grupo: str
    tipo_cifrado: str
    mensaje: str

class MiembroAgregarRequest(BaseModel):
    id_grupo: int
    id_usuario: int

class MiembroAgregarResponse(BaseModel):
    id_pk: int
    id_grupo_fk: int
    id_user_fk: int
    mensaje: str

class MessageIndidualRequest(BaseModel):
    mensaje: str
    clave_aes_cifrada: str
    firma: str
    hash_mensaje: str

class MessageIndividualResponse(BaseModel):
    message: str
    timestamp: datetime

class MessageIndividualRequestSimplified(BaseModel):
    mensaje: str
    clave_privada: str

class MessageReceived(BaseModel):
    id: int
    message: str
    firma: str
    hash_mensaje: str
    clave_aes_cifrada: str
    timestamp: datetime
    remitente: str

    class Config:
        orm_mode = True
