from .auth import router as auth_router
from .mensajes import router as messages_router
from .grupos import router as grupos_router
from .firmas import router as firmas_router

__all__ = [
    "auth_router",
    "messages_router",
    "grupos_router",
    firmas_router
]