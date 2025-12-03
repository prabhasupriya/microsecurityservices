import base64
import pyotp


# ---------------------------------------------------
# HEX -> BASE32 conversion used by both functions
# ---------------------------------------------------
def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed to base32 string
    """

    # Step 1: Convert hex string to bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # Step 2: Convert bytes to Base32
    base32_seed = base64.b32encode(seed_bytes)

    # Step 3: Convert bytes -> string
    return base32_seed.decode("utf-8")


# ---------------------------------------------------
# Generate TOTP code
# ---------------------------------------------------
def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed

    Args:
        hex_seed: 64-character hex string

    Returns:
        6-digit TOTP code string
    """

    # Convert hex -> base32
    base32_seed = hex_to_base32(hex_seed)

    # Create TOTP
    totp = pyotp.TOTP(
        s=base32_seed,
        digits=6,
        interval=30
    )

    # Generate current OTP
    return totp.now()


# ---------------------------------------------------
# Verify TOTP
# ---------------------------------------------------
def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with tolerance window

    Args:
        hex_seed: 64-character hex string
        code: OTP code to verify
        valid_window: ±period window (default ±30s)

    Returns:
        True or False
    """

    # Convert hex -> base32
    base32_seed = hex_to_base32(hex_seed)

    # Create TOTP
    totp = pyotp.TOTP(
        s=base32_seed,
        digits=6,
        interval=30
    )

    # Verify OTP
    return totp.verify(code, valid_window=valid_window)


# ---------------------------------------------------
# LOCAL TEST RUN
# ---------------------------------------------------
if __name__ == "__main__":

    # Load decrypted seed from Step 5 output
    with open("data/seed.txt", "r") as f:
        hex_seed = f.read().strip()

    # Generate OTP
    code = generate_totp_code(hex_seed)

    print("Generated TOTP Code:", code)

    # Verify OTP
    result = verify_totp_code(hex_seed, code)

    print(" Verification result:", result)
