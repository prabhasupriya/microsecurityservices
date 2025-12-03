#!/usr/bin/env python3

import os
import base64
from datetime import datetime, timezone
from totp_utils import generate_totp_code  # import your existing helper

SEED_PATH = "/data/seed.txt"

def main():
    # 1. Read hex seed
    if not os.path.exists(SEED_PATH):
        print("Seed not found. Skipping.")
        return

    try:
        with open(SEED_PATH, "r") as f:
            hex_seed = f.read().strip()
    except Exception as e:
        print(f"Failed to read seed: {e}")
        return

    # 2. Generate TOTP code
    try:
        code = generate_totp_code(hex_seed)
    except Exception as e:
        print(f"Failed to generate TOTP code: {e}")
        return

    # 3. Get current UTC timestamp
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # 4. Output log line
    print(f"{timestamp} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
