from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair

    Returns:
        Tuple of (private_key, public_key) objects

    Implementation:
    - Generate 4096-bit RSA key
    - Use public exponent 65537
    - Serialize keys to PEM format
    - Save to files
    """

    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

    # Get public key from private key
    public_key = private_key.public_key()

    # Serialize PRIVATE key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize PUBLIC key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Write PRIVATE key to file (MUST COMMIT)
    with open("student_private.pem", "wb") as private_file:
        private_file.write(private_pem)

    # Write PUBLIC key to file (MUST COMMIT)
    with open("student_public.pem", "wb") as public_file:
        public_file.write(public_pem)

    print(" RSA 4096-bit key pair generated successfully!")
    print(" Files created:")
    print("   - student_private.pem")
    print("   - student_public.pem")

    return private_key, public_key


# Run generation directly
if __name__ == "__main__":
    generate_rsa_keypair()
