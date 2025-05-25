from pydantic import BaseModel
from datetime import datetime

class MessageIndidualRequest(BaseModel):
    mensaje: str
    clave_aes_cifrada: str
    firma: str
    hash_mensaje: str

class MessageIndividualResponse(BaseModel):
    message: str
    timestamp: datetime

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
