from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Tabla Usuarios
class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    llave_publica = Column(String, nullable=False)
    hash_clave_privada = Column(String, nullable=False)
    metodo_autenticacion = Column(String, nullable=False)

    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre={self.nombre})>"

# Tabla Mensajes
class Mensaje(Base):
    __tablename__ = 'mensajes'

    id = Column(Integer, primary_k=True, autoincrement=True)
    emisor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    receptor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    mensaje_cifrado = Column(LargeBinary, nullable=False)
    firma_digital = Column(LargeBinary, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones con la tabla Usuario
    emisor = relationship("Usuario", foreign_keys=[emisor_id])
    receptor = relationship("Usuario", foreign_keys=[receptor_id])

    def __repr__(self):
        return f"<Mensaje(id={self.id}, emisor_id={self.emisor_id}, receptor_id={self.receptor_id})>"

# Tabla Grupos
class Grupo(Base):
    __tablename__ = 'grupos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    clave_AES_cifrada = Column(String, nullable=False)
    
    # Relacion con Usuarios (usuarios que pertenecen al grupo)
    usuarios = relationship("Usuario", secondary='grupo_usuario', backref='grupos')

    def __repr__(self):
        return f"<Grupo(id={self.id}, clave_AES_cifrada={self.clave_AES_cifrada})>"

# Tabla de relación entre Grupos y Usuarios
class GrupoUsuario(Base):
    __tablename__ = 'grupo_usuario'

    grupo_id = Column(Integer, ForeignKey('grupos.id'), primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), primary_key=True)

    def __repr__(self):
        return f"<GrupoUsuario(grupo_id={self.grupo_id}, usuario_id={self.usuario_id})>"

# Tabla Blockchain
class Blockchain(Base):
    __tablename__ = 'blockchain'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transacciones = Column(String, nullable=False)

    def __repr__(self):
        return f"<Blockchain(id={self.id}, transacciones={self.transacciones})>"
