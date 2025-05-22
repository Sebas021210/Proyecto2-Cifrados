from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

def sign_message(private_key_pem: bytes, message: bytes) -> bytes:
    """Firma un mensaje con ECDSA usando SHA-256."""
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
    return signature

def verify_signature(public_key_pem: bytes, message: bytes, signature: bytes) -> bool:
    """Verifica la firma usando la clave pública ECDSA."""
    public_key = serialization.load_pem_public_key(public_key_pem)
    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False
