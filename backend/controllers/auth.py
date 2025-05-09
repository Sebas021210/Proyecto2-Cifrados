import hashlib
from backend.database import db, User
from backend.controllers.keys import generate_rsa_keys, generate_ecc_keys
import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
from fastapi import HTTPException, Header, Depends

SECRET_KEY = "clave_secreta_super_segura"


"""
----------------------- JWT -----------------------

"""
SECRET_KEY = "clave_secreta_super_segura"

from datetime import datetime, timedelta, timezone

def _generate_jwt_token(user: User) -> str:
    """Genera un JWT con el ID del usuario y una expiración de 1 hora."""
    now = datetime.now(timezone.utc)  # <-- UTC explícito
    payload = {
        "user_id": user.email,
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "iat": int(now.timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt(token: str) -> User:
    """Verifica el JWT y devuelve el usuario asociado."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("user_id")

        if not email:
            raise HTTPException(status_code=401, detail="Token inválido: sin usuario")

        user = get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        return user

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except DecodeError:
        raise HTTPException(status_code=401, detail="Token inválido")


def get_current_user(authorization: str = Header(...)) -> User:
    """Obtiene el usuario actual a partir del JWT en el encabezado de autorización."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Formato de autorización inválido")
    token = authorization.split(" ")[1]
    return verify_jwt(token)

"""

----------------------- AUTH -----------------------

"""

def _hash_password(password: str) -> str:
    """Hashea la contraseña con SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_email(email: str) -> User:
    """Obtiene un usuario por su correo electrónico."""
    with db.read() as session:
        return session.query(User).filter_by(email=email).first()


def register(email: str, password: str) -> User:
    """Crea un nuevo usuario con la contraseña hasheada usando SHA-256."""
    hashed_password = _hash_password(password)
    with db.write() as session:
        user = User(email=email, password=hashed_password)
        session.add(user)
        session.commit()
        return user


def login(email: str, password: str) -> tuple[str, str]:
    """Inicia sesión y devuelve email + token si las credenciales son válidas."""

    with db.write() as session:
        user = session.query(User).filter_by(email=email).first()

        if not user or user.password != _hash_password(password):
            return "", ""

        token = _generate_jwt_token(user)
        return user.email, token




if __name__ == "__main__":
    # Test the functions
    try:
        register(email="test@email.com", password="password123")
    except Exception as e:
        print(f"Error creating user: {e}")

    print(login(email="test@email.com", password="password123"))
