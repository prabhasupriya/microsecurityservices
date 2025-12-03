# api.py
from fastapi import FastAPI
from pydantic import BaseModel
import base64

app = FastAPI()

class SeedRequest(BaseModel):
    encrypted_seed: str

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/decrypt-seed")
def decrypt_seed(request: SeedRequest):
    try:
        decoded_bytes = base64.b64decode(request.encrypted_seed)
        # Return as base64 or hex
        return {
            "status": "ok",
            "decrypted_seed_base64": base64.b64encode(decoded_bytes).decode('utf-8'),
            "decrypted_seed_hex": decoded_bytes.hex()
        }
    except Exception as e:
        return {"error": str(e)}

