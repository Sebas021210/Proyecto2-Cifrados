from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import hashlib, base64
import os

def calcular_hash_mensaje(mensaje: str, algoritmo: str = "sha256") -> str:
    if algoritmo == "sha256":
        return hashlib.sha256(mensaje.encode()).hexdigest()
    elif algoritmo == "sha3_256":
        return hashlib.sha3_256(mensaje.encode()).hexdigest()
    else:
        raise ValueError("Algoritmo de hash no soportado")

def sign_message(private_key_pem: str, message: str) -> str:
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    signature = private_key.sign(message.encode(), ec.ECDSA(hashes.SHA256()))
    return signature.hex()

def verify_signature(public_key_pem: str, message: str, signature_hex: str) -> bool:
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    signature = bytes.fromhex(signature_hex)
    try:
        public_key.verify(signature, message.encode(), ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False

def generate_aes_key():
    return os.urandom(32)

def generate_ecc_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ).decode()

    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return {
        "private_key": private_pem,
        "public_key": public_pem
    }

def encrypt_message_aes(message: str, aes_key: bytes) -> dict:
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)
    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(nonce).decode()
    }

def encrypt_aes_key_with_ecc(aes_key: bytes, peer_public_key_pem: str) -> dict:
    peer_public_key = serialization.load_pem_public_key(peer_public_key_pem.encode())
    ephemeral_private_key = ec.generate_private_key(ec.SECP256R1())
    shared_key = ephemeral_private_key.exchange(ec.ECDH(), peer_public_key)

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ecies",
    ).derive(shared_key)

    aesgcm = AESGCM(derived_key)
    nonce = os.urandom(12)
    encrypted_key = aesgcm.encrypt(nonce, aes_key, None)
    ephemeral_public_key = ephemeral_private_key.public_key()
    ephemeral_pem = ephemeral_public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return {
        "encrypted_key": base64.b64encode(encrypted_key).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ephemeral_public_key": ephemeral_pem
    }