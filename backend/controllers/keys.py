from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import hashlib
from cryptography.hazmat.primitives import hashes as crypto_hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1

def save_hash(file_data: bytes, file_path: str, method: str) -> str:
    """Calcula el hash del archivo y lo guarda en un archivo txt con el método de firma."""
    file_hash = hashlib.sha256(file_data).hexdigest()
    hash_file_path = f"{file_path}.{method}.hash"  # Guardamos con el método de firma en el nombre
    with open(hash_file_path, "w") as f:
        f.write(f"SHA256: {file_hash}\nFirmado con: {method}")

    return hash_file_path


def sign_file_with_rsa(file_path: str, private_key_obj: rsa.RSAPrivateKey) -> tuple:
    """Firma el archivo utilizando un objeto de clave privada RSA y guarda el hash."""
    with open(file_path, "rb") as f:
        file_data = f.read()

    # Generar la firma del archivo
    signature = private_key_obj.sign(
        file_data,
        PSS(mgf=MGF1(crypto_hashes.SHA256()), salt_length=PSS.MAX_LENGTH),
        crypto_hashes.SHA256()
    )

    # Guardar la firma en un archivo
    signature_path = f"{file_path}.rsa.sig"
    with open(signature_path, "wb") as f:
        f.write(signature)

    # Guardar el hash con el método 'rsa'
    hash_file_path = save_hash(file_data, file_path, "rsa")

    return signature_path, hash_file_path


def sign_file_with_ecc(file_path: str, private_key_obj: ec.EllipticCurvePrivateKey) -> tuple:
    """Firma el archivo utilizando un objeto de clave privada ECC y guarda el hash."""
    with open(file_path, "rb") as f:
        file_data = f.read()

    # Generar la firma del archivo
    signature = private_key_obj.sign(
        file_data,
        ec.ECDSA(crypto_hashes.SHA256())
    )

    # Guardar la firma en un archivo
    signature_path = f"{file_path}.ecc.sig"
    with open(signature_path, "wb") as f:
        f.write(signature)

    # Guardar el hash con el método 'ecc'
    hash_file_path = save_hash(file_data, file_path, "ecc")

    return signature_path, hash_file_path

def generate_rsa_keys():
    """Genera un par de claves RSA (2048 bits) y retorna clave privada y pública."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # Serializar claves
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode(), public_pem.decode()


def generate_ecc_keys():
    """Genera un par de claves ECC (secp256r1) y retorna clave privada y pública."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # Serializar claves
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode(), public_pem.decode()

def generate_keys():
    """Genera un par de claves RSA y ECC y retorna ambas claves privadas y públicas."""
    rsa_private, rsa_public = generate_rsa_keys()
    ecc_private, ecc_public = generate_ecc_keys()

    return {
        "rsa": {
            "private": rsa_private,
            "public": rsa_public
        },
        "ecc": {
            "private": ecc_private,
            "public": ecc_public
        }
    }