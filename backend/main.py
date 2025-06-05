from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
from backend.routes import auth_router, blockchain, messages_router, grupos_router, firmas_router


app = FastAPI(
    title="Cifrados: Proyecto 2 - Blockchain y Cifrado",
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(messages_router, prefix="/msg", tags=["mensajes"])

app.include_router(grupos_router, prefix="/grupos", tags=["grupos"])

app.include_router(firmas_router, prefix="/firmas", tags=["firmas"])

app.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
