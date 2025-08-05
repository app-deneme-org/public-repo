import jwt
import time
import requests
import base64
import nacl.encoding
import nacl.public

# --- Bilgiler ---
APP_ID = 1642218
INSTALLATION_ID = 76915481
PRIVATE_KEY_PATH = "/home/ysufemrlty/Downloads/deneme-app-test-org.2025-07-21.private-key.pem"
OWNER = "app-deneme-org"  # Organization name
REPO = "public-repo"      # Secret yazılacak repo
SECRET_NAME = "PYTHON_TOKEN"

# --- JWT oluştur ---
with open(PRIVATE_KEY_PATH, "r") as key_file:
    private_key = key_file.read()

now = int(time.time())
payload = {
    "iat": now,
    "exp": now + (10 * 60),
    "iss": APP_ID
}

jwt_token = jwt.encode(payload, private_key, algorithm="RS256")

# --- Installation Access Token al ---
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
    exit()

# --- Public Key Al (Repo için) ---
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}
url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/public-key"
res = requests.get(url, headers=headers)

if res.status_code != 200:
    print("Public key alınamadı:", res.status_code, res.text)
    exit()

key_id = res.json()["key_id"]
public_key = res.json()["key"]

# --- Secret'ı şifrele ---
def encrypt_secret(public_key: str, secret_value: str) -> str:
    public_key_bytes = base64.b64decode(public_key)
    sealed_box = nacl.public.SealedBox(nacl.public.PublicKey(public_key_bytes))
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

encrypted_token = encrypt_secret(public_key, token)

# --- Secret'ı gönder (Repo'ya) ---
put_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/{SECRET_NAME}"
data = {
    "encrypted_value": encrypted_token,
    "key_id": key_id
}
put_res = requests.put(put_url, headers=headers, json=data)

if put_res.status_code in [201, 204]:
    print(f"✅ Secret '{SECRET_NAME}' başarıyla güncellendi.")
else:
    print("❌ Secret güncellenemedi:", put_res.status_code, put_res.text)
