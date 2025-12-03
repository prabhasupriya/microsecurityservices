#!/usr/bin/env python3

import sys
sys.path.append("/app")   # ✅ THIS FIX MAKES Python FIND totp_service.py

from datetime import datetime
from totp_service import generate_totp_code

SEED_FILE = "/data/seed.txt"
OUTPUT_FILE = "/cron/last_code.txt"

def main():
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
    except FileNotFoundError:
        with open(OUTPUT_FILE, "a") as f:
            f.write(f"{datetime.utcnow()} - Seed file not found\n")
        return

    code = generate_totp_code(hex_seed)
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with open(OUTPUT_FILE, "a") as f:
        f.write(f"{timestamp} - 2FA Code: {code}\n")

if __name__ == "__main__":
    main()
