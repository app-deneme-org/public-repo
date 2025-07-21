import jwt
import time
import requests

# --- Bilgiler ---
APP_ID = 1642218  # GitHub App ID'nizi buraya yazın (integer)
INSTALLATION_ID = 76915481  # Organizasyona kurulum ID'si (integer)
PRIVATE_KEY_PATH = "/home/ysufemrlty/Downloads/deneme-app-test-org.2025-07-21.private-key.pem"

# --- JWT oluştur ---
with open(PRIVATE_KEY_PATH, "r") as key_file:
    private_key = key_file.read()

now = int(time.time())
payload = {
    "iat": now,           # oluşturulma zamanı
    "exp": now + (10 * 60),  # 10 dakika geçerli
    "iss": APP_ID         # App ID
}

jwt_token = jwt.encode(payload, private_key, algorithm="RS256")

# --- Installation Access Token almak için API çağrısı ---
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Accept": "application/vnd.github+json"
}

url = f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens"

response = requests.post(url, headers=headers)

if response.status_code == 201:
    token = response.json()["token"]
    expires_at = response.json()["expires_at"]
    print(f"Access Token: {token}")
    print(f"Expires at: {expires_at}")
else:
    print("Hata oluştu:", response.status_code, response.text)
