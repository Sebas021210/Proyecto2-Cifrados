from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, DateTime
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
    hash = Column(String, nullable=False)
    contraseña = Column(String, nullable=False)
    nombre = Column(String, nullable=False)

# Tabla Mensajes
class Mensajes(Base):
    __tablename__ = 'mensajes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_bloque = Column(Integer, ForeignKey('blockchain_grupo.id_bloque_pk'))
    id_remitente = Column(Integer, ForeignKey('user.id_pk'))
    id_receptor = Column(Integer, ForeignKey('user.id_pk'))
    mensaje = Column(String, nullable=False)
    firma = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    remitente = relationship("User", foreign_keys=[id_remitente])
    receptor = relationship("User", foreign_keys=[id_receptor])

# Tabla Blockchain Grupo (para mensajes individuales también)
class BlockchainGrupo(Base):
    __tablename__ = 'blockchain_grupo'

    id_bloque_pk = Column(Integer, primary_key=True, autoincrement=True)
    hash_anterior = Column(String, nullable=False)
    hash_actual = Column(String, nullable=False)
    nonce = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)

# Tabla Grupos
class Grupos(Base):
    __tablename__ = 'grupos'

    id_pk = Column(Integer, primary_key=True, autoincrement=True)
    nombre_de_grupo = Column(String, nullable=False)
    llave_publica = Column(String, nullable=False)

# Tabla miembros de grupos
class MiembrosGrupos(Base):
    __tablename__ = 'miembros_de_grupos'

    id_pk = Column(Integer, primary_key=True, autoincrement=True)
    id_grupo_fk = Column(Integer, ForeignKey('grupos.id_pk'))
    id_user_fk = Column(Integer, ForeignKey('user.id_pk'))

# Tabla Mensajes Grupo
class MensajesGrupo(Base):
    __tablename__ = 'mensajes_grupo'

    id_transacciones_pk = Column(Integer, primary_key=True, autoincrement=True)
    id_bloque_grupo = Column(Integer, ForeignKey('blockchain_grupo.id_bloque_pk'))
    id_grupo_fk = Column(Integer, ForeignKey('grupos.id_pk'))
    id_remitente_fk = Column(Integer, ForeignKey('user.id_pk'))
    mensaje = Column(String, nullable=False)
    firma = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    remitente = relationship("User", foreign_keys=[id_remitente_fk])
    grupo = relationship("Grupos", foreign_keys=[id_grupo_fk])
    bloque = relationship("BlockchainGrupo", foreign_keys=[id_bloque_grupo])
