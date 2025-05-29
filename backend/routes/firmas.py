from fastapi import APIRouter, Depends, HTTPException
from backend.models.message import FirmaRequest, VerificacionRequest, MensajeSolo
from backend.controllers.firma import sign_message, verify_signature, generate_ecc_key_pair, generate_aes_key, calcular_hash_mensaje
import base64

router = APIRouter()

@router.post("/firmar")
def firmar(request: FirmaRequest):
    signature = sign_message(request.private_key, request.message)
    return {"firma": signature}

@router.post("/verificar")
def verificar(request: VerificacionRequest):
    is_valid = verify_signature(request.public_key, request.message, request.signature)
    return {"valida": is_valid}

@router.get("/generar-claves")
def generar_todas_las_claves():
    aes_key = generate_aes_key()
    ecc_keys = generate_ecc_key_pair()

    return {
        "aes_key_base64": base64.b64encode(aes_key).decode(),
        "ecc": {
            "private_key": ecc_keys["private_key"],
            "public_key": ecc_keys["public_key"]
        }
    }

@router.post("/hash")
def obtener_hash(request: MensajeSolo, algoritmo: str = "sha256"):
    try:
        digest = calcular_hash_mensaje(request.message, algoritmo)
        return {"hash": digest, "algoritmo": algoritmo}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
