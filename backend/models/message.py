from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class FirmaRequest(BaseModel):
    private_key: str
    message: str

class VerificacionRequest(BaseModel):
    public_key: str
    message: str
    signature: str

class MensajeSolo(BaseModel):
    message: str

# schemas.py

class GrupoCreateRequest(BaseModel):
    nombre: str
    miembros_ids: Optional[List[int]] = []


class GrupoCreateResponse(BaseModel):
    id_pk: int
    nombre_de_grupo: str
    tipo_cifrado: str
    llave_privada: str
    mensaje: str


class GrupoListItem(BaseModel):
    id_pk: int
    nombre_de_grupo: str
    tipo_cifrado: str

    class Config:
        orm_mode = True

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
    clave_privada_pem: str

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

class MiembroDetalle(BaseModel):
    id: int
    nombre: str
    correo: str

    class Config:
        orm_mode = True

class MiembroDetalleMono(BaseModel):
    id: int
    nombre: str
    correo: str
    llave_privada_cifrada: Optional[str] = None

    class Config:
        orm_mode = True

class GrupoDetalleResponse(BaseModel):
    id_pk: int
    nombre_de_grupo: str
    tipo_cifrado: str
    miembros: list[MiembroDetalle]

    class Config:
        orm_mode = True

class UserListItem(BaseModel):
    id_pk: int
    nombre: str
    correo: str
    public_key: str

    class Config:
        orm_mode = True


class MiembroEliminarRequest(BaseModel):
    id_grupo: int
    id_usuario: int

class GroupMessageRequest(BaseModel):
    mensaje: str
    clave_privada_usuario_pem: str  # PEM para firmar mensaje plano

class MensajeGrupoResponse(BaseModel):
    id_transaccion: int
    remitente: str
    mensaje: str
    nonce: str
    clave_aes_cifrada: str
    firma: str
    timestamp: str

class DescifrarRequest(BaseModel):
    group_id: int
    user_private_key_pem: str  # La llave privada PEM del usuario

class DescifrarResponse(BaseModel):
    llave_privada_grupo: str

class DecryptGroupMessageRequest(BaseModel):
    mensaje_cifrado: str
    nonce: str
    clave_aes_cifrada: Dict[str, str]  # contiene 'aes_key_encrypted', 'nonce', 'ephemeral_public_key'
    private_key_grupo_pem: str

class DecryptGroupMessageResponse(BaseModel):
    mensaje_plano: str
