from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import base64
import subprocess

# -------- Sign commit hash using RSA-PSS --------
def sign_message(message: str, private_key) -> bytes:
    """
    Sign a message using RSA-PSS with SHA-256
    """
    signature = private_key.sign(
        message.encode('utf-8'),  # ASCII/UTF-8 bytes
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# -------- Encrypt with RSA-OAEP --------
def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA-OAEP with SHA-256
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# -------- Load keys from PEM files --------
def load_private_key(file_path: str):
    with open(file_path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

def load_public_key(file_path: str):
    with open(file_path, "rb") as f:
        return serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )

# -------- Get current commit hash --------
def get_latest_commit_hash():
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()  # 40-char hex string

# -------- Full commit proof generation --------
def generate_commit_proof(student_private_path, instructor_public_path):
    commit_hash = get_latest_commit_hash()
    print("Commit Hash:", commit_hash)

    # Load keys
    student_private = load_private_key(student_private_path)
    instructor_public = load_public_key(instructor_public_path)

    # Sign commit hash
    signature = sign_message(commit_hash, student_private)

    # Encrypt signature
    encrypted_sig = encrypt_with_public_key(signature, instructor_public)

    # Base64 encode
    encoded_sig = base64.b64encode(encrypted_sig).decode('utf-8')
    print("Encrypted Signature (Base64):", encoded_sig)
    return commit_hash, encoded_sig

# Example usage
commit_hash, encrypted_signature = generate_commit_proof(
    "student_private.pem",
    "instructor_public.pem"
)
