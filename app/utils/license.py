from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import base64
import json
from app.config import settings

# Generate a key for encryption and decryption
def generate_key():
    return Fernet.generate_key()

# Encrypt the data
def encrypt_data(data: dict, key: bytes):
    fernet = Fernet(key)
    data_str = json.dumps(data)
    encrypted_data = fernet.encrypt(data_str.encode())
    return base64.urlsafe_b64encode(encrypted_data).decode()

# Decrypt the data
def decrypt_data(token: str, key: bytes):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(base64.urlsafe_b64decode(token.encode()))
    return json.loads(decrypted_data.decode())

# Generate a license key
def generate_license_key(user_info: dict, duration: timedelta):
    key = settings.SECRET_KEY.encode()  # Use the secret key from settings
    if len(key) != 32:
        key = generate_key() 
    expire_date = (datetime.now() + duration).isoformat()
    data = {
        "user_info": user_info,
        "expire_date": expire_date
    }
    return encrypt_data(data, key)

# Extract information from a license key
def extract_license_key(token: str):
    key = settings.SECRET_KEY.encode()  # Use the secret key from settings
    data = decrypt_data(token, key)
    user_info = data["user_info"]
    expire_date = datetime.fromisoformat(data["expire_date"])
    return user_info, expire_date