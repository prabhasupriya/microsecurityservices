import base64
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP

    Args:
        encrypted_seed_b64: Base64-encoded ciphertext
        private_key: RSA private key object

    Returns:
        Decrypted hex seed (64-character string)

    Steps:
    1. Base64 decode
    2. Decrypt using RSA-OAEP
       - OAEP padding
       - MGF1(SHA256)
       - SHA256
       - No label
    3. Convert bytes to UTF-8 text
    4. Validate hex string (length = 64)
    5. Return seed
    """

    # --------------------
    # Step 1: Decode Base64
    # --------------------
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # --------------------
    # Step 2: RSA-OAEP Decrypt
    # --------------------
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # --------------------
    # Step 3: Decode to string
    # --------------------
    decrypted_seed = decrypted_bytes.decode("utf-8")

    # --------------------
    # Step 4: Validate seed
    # --------------------
    if len(decrypted_seed) != 64:
        raise ValueError(" Invalid seed length. Must be 64 characters.")

    hex_chars = "0123456789abcdef"
    for c in decrypted_seed:
        if c not in hex_chars:
            raise ValueError("Seed contains non-hex characters.")

    return decrypted_seed


# -------------------------------------------------

if __name__ == "__main__":

    # --------------------
    # Load PRIVATE KEY
    # --------------------
    with open("student_private.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    # --------------------
    # Load encrypted seed received in STEP 4
    # --------------------
    with open("encrypted_seed.txt", "r") as f:
        encrypted_seed = f.read().strip()

    # --------------------
    # Run decryption
    # --------------------
    seed = decrypt_seed(encrypted_seed, private_key)

    print(" Decrypted seed successfully:")
    print(seed)

    # --------------------
    # Save to /data/seed.txt
    # --------------------
    os.makedirs("data", exist_ok=True)

    with open("data/seed.txt", "w") as f:
        f.write(seed)

    print(" Seed saved to: data/seed.txt")
