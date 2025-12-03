import os
import base64
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

import pyotp


# ----------------------------------------------------
# CONSTANTS
# ----------------------------------------------------
PRIVATE_KEY_FILE = "student_private.pem"
SEED_FILE = "data/seed.txt"


# ----------------------------------------------------
# APP
# ----------------------------------------------------
app = FastAPI(title="Secure PKI 2FA Microservice")


# ----------------------------------------------------
# MODELS
# ----------------------------------------------------
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class VerifyCodeRequest(BaseModel):
    code: str


# ----------------------------------------------------
# UTILITY FUNCTIONS
# ----------------------------------------------------
def load_private_key():
    with open(PRIVATE_KEY_FILE, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )


def decrypt_seed(encrypted_seed_b64: str) -> str:
    private_key = load_private_key()

    # Decode BASE64
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # Decrypt using RSA-OAEP SHA256
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    seed = decrypted_bytes.decode("utf-8")

    # Validate: 64 hex chars
    if len(seed) != 64:
        raise ValueError("Invalid seed length")

    valid_chars = "0123456789abcdef"
    if not all(c in valid_chars for c in seed):
        raise ValueError("Seed not hex")

    return seed


def hex_to_base32(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode()


def generate_totp(hex_seed: str) -> str:
    base32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32, digits=6, interval=30)
    return totp.now()


def verify_totp(hex_seed: str, code: str) -> bool:
    base32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32, digits=6, interval=30)
    
    # ±1 time window tolerance
    return totp.verify(code, valid_window=1)


# ----------------------------------------------------
# ENDPOINT 1: /decrypt-seed
# ----------------------------------------------------
@app.post("/decrypt-seed")
def decrypt_seed_endpoint(req: DecryptSeedRequest):

    try:
        # Decrypt seed
        seed = decrypt_seed(req.encrypted_seed)

        # Save seed
        os.makedirs("data", exist_ok=True)

        with open(SEED_FILE, "w") as f:
            f.write(seed)

        return {"status": "ok"}

    except Exception as e:
        print("Decryption error:", e)
        raise HTTPException(
            status_code=500,
            detail="Decryption failed"
        )


# ----------------------------------------------------
# ENDPOINT 2: /generate-2fa
# ----------------------------------------------------
@app.get("/generate-2fa")
def generate_2fa_endpoint():

    if not os.path.exists(SEED_FILE):
        raise HTTPException(
            status_code=500,
            detail="Seed not decrypted yet"
        )

    try:
        # Read seed
        with open(SEED_FILE, "r") as f:
            seed = f.read().strip()

        # Generate code
        code = generate_totp(seed)

        # Compute validity remaining
        seconds = int(time.time()) % 30
        remaining = 30 - seconds

        return {
            "code": code,
            "valid_for": remaining
        }

    except Exception as e:
        print("Generate error:", e)
        raise HTTPException(
            status_code=500,
            detail="Seed not decrypted yet"
        )


# ----------------------------------------------------
# ENDPOINT 3: /verify-2fa
# ----------------------------------------------------
@app.post("/verify-2fa")
def verify_2fa_endpoint(req: VerifyCodeRequest):

    # Validate input
    if not req.code:
        raise HTTPException(
            status_code=400,
            detail="Missing code"
        )

    if not os.path.exists(SEED_FILE):
        raise HTTPException(
            status_code=500,
            detail="Seed not decrypted yet"
        )

    # Read seed
    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()

    try:
        result = verify_totp(seed, req.code)

        return {
            "valid": result
        }

    except Exception as e:
        print("Verify error:", e)
        raise HTTPException(
            status_code=500,
            detail="Seed not decrypted yet"
        )
