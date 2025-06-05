from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Tabla User
class User(Base):
    __tablename__ = 'user'

    id_pk = Column(Integer, primary_key=True, autoincrement=True)
    public_key = Column(String, nullable=False)
    correo = Column(String, nullable=False)
    contraseña = Column(String, nullable=True)
    nombre = Column(String, nullable=False)
    hash = Column(String, nullable=True)

# Tabla Blockchain general (única)
class Blockchain(Base):
    __tablename__ = 'blockchain'

    id_bloque_pk = Column(Integer, primary_key=True, autoincrement=True)
    hash_anterior = Column(String, nullable=False)
    hash_actual = Column(String, nullable=False)
    nonce = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)

    # Relaciones inversas (opcional pero útil)
    mensajes = relationship("Mensajes", back_populates="bloque")
    mensajes_grupo = relationship("MensajesGrupo", back_populates="bloque")

# Tabla Mensajes (individuales)
class Mensajes(Base):
    __tablename__ = 'mensajes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_bloque = Column(Integer, ForeignKey('blockchain.id_bloque_pk'))
    id_remitente = Column(Integer, ForeignKey('user.id_pk'))
    id_receptor = Column(Integer, ForeignKey('user.id_pk'))
    mensaje = Column(String, nullable=False)
    firma = Column(String, nullable=False)
    clave_aes = Column(LargeBinary, nullable=True)
    clave_aes_cifrada = Column(String, nullable=False)
    hash_mensaje = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    remitente = relationship("User", foreign_keys=[id_remitente])
    receptor = relationship("User", foreign_keys=[id_receptor])
    bloque = relationship("Blockchain", back_populates="mensajes")

# Tabla Grupos
class Grupos(Base):
    __tablename__ = 'grupos'

    id_pk = Column(Integer, primary_key=True, autoincrement=True)
    nombre_de_grupo = Column(String, nullable=False)
    llave_publica = Column(String, nullable=False)
    tipo_cifrado = Column(String, nullable=False)

    miembros_grupo = relationship("MiembrosGrupos", back_populates="grupo")

# Tabla miembros de grupos
class MiembrosGrupos(Base):
    __tablename__ = 'miembros_de_grupos'

    id_pk = Column(Integer, primary_key=True, autoincrement=True)
    id_grupo_fk = Column(Integer, ForeignKey('grupos.id_pk'))
    id_user_fk = Column(Integer, ForeignKey('user.id_pk'))

    llave_privada_grupo_cifrada = Column(LargeBinary, nullable=True)  # NUEVO CAMPO

    grupo = relationship("Grupos", back_populates="miembros_grupo")
    usuario = relationship("User", backref="grupos_pertenecientes")

# Tabla Mensajes Grupo
class MensajesGrupo(Base):
    __tablename__ = 'mensajes_grupo'

    id_transacciones_pk = Column(Integer, primary_key=True, autoincrement=True)
    id_bloque_grupo = Column(Integer, ForeignKey('blockchain.id_bloque_pk'))
    id_grupo_fk = Column(Integer, ForeignKey('grupos.id_pk'))
    id_remitente_fk = Column(Integer, ForeignKey('user.id_pk'))

    mensaje = Column(String, nullable=False)  # Mensaje cifrado AES-GCM (base64)
    nonce = Column(String, nullable=False)    # Nonce AES-GCM (base64)
    clave_aes_cifrada = Column(String, nullable=False)  # AES key cifrada con clave pública grupo (base64 o JSON)
    firma = Column(String, nullable=False)    # Firma ECDSA (hex)
    hash_mensaje = Column(String, nullable=False)  # Hash del mensaje plano (hex)
    timestamp = Column(DateTime, default=datetime.utcnow)

    remitente = relationship("User", foreign_keys=[id_remitente_fk])
    grupo = relationship("Grupos", foreign_keys=[id_grupo_fk])
    bloque = relationship("Blockchain", back_populates="mensajes_grupo")
