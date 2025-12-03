import requests


API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"


def request_seed(student_id: str, github_repo_url: str, api_url: str):
    """
    Request encrypted seed from instructor API

    Steps implemented:

    1. Read student public key from PEM file
    2. Prepare JSON payload
    3. Send POST request
    4. Parse response
    5. Save encrypted seed to encrypted_seed.txt (NOT committed to Git)
    """

    # --------------------------
    # Step 1: Read public key
    # --------------------------
    with open("student_public.pem", "r") as file:
        public_key = file.read()

    # NOTE:
    # PEM format already includes \n newlines.
    # requests library handles newlines automatically

    # --------------------------
    # Step 2: Prepare payload
    # --------------------------
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key
    }

    # --------------------------
    # Step 3: Send POST request
    # --------------------------
    response = requests.post(
        api_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=15
    )

    if response.status_code != 200:
        print("❌ API ERROR")
        print(response.text)
        return

    # --------------------------
    # Step 4: Parse response
    # --------------------------
    data = response.json()

    if data.get("status") != "success":
        print("❌ API returned failure:")
        print(data)
        return

    encrypted_seed = data["encrypted_seed"]

    # --------------------------
    # Step 5: Save seed to file
    # --------------------------
    with open("encrypted_seed.txt", "w") as file:
        file.write(encrypted_seed)

    print("✅ SUCCESS!")
    print("Encrypted seed saved in encrypted_seed.txt")


# --------------------------
# RUN SCRIPT
# --------------------------
if __name__ == "__main__":
    STUDENT_ID = "23A91A6106"
    GITHUB_REPO = "https://github.com/prabhasupriya/microsecurityservices.git"

    request_seed(STUDENT_ID, GITHUB_REPO, API_URL)
