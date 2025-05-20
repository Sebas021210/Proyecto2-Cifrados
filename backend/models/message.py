from pydantic import BaseModel
from datetime import datetime

class MessageIndidualRequest(BaseModel):
    id_remitente: int
    id_receptor: int
    mensaje: str
    clave_aes_cifrada: str
    firma: str
    hash_mensaje: str

class MessageIndividualResponse(BaseModel):
    message: str
    timestamp: datetime
