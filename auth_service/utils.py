import hashlib
import hmac
import base64
import json
import os

from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set")

def hmac_sha256(message):
    # used https://nutbutterfly.medium.com/how-to-sign-your-message-with-hmac-sha256-in-python-and-java-e7d8d055087e as a reference
    """Encodes a message and secret into a hmac_sha256 string."""
    return hmac.new(SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()

def base64_encode(byte_input):
    # used https://www.geeksforgeeks.org/base64-urlsafe_b64encodes-in-python/ as reference
    """Encodes byte input into a Base64 string."""
    return base64.urlsafe_b64encode(byte_input).decode('utf-8').rstrip('=')

def construct_jwt(header, payload):
    # used https://jwt.io/introduction as reference
    message = base64_encode(header.encode("utf-8")) + '.' + base64_encode(payload.encode("utf-8")) 
    signature = hmac_sha256(message)
    jwt = message + '.' + base64_encode(signature)
    return jwt

def generate_jwt(username):
    header = json.dumps({"alg": "HS256", "typ": "JWT"})
    payload = json.dumps({"sub": "auth", "name": username, "admin": True})
    return construct_jwt(header,payload)

def add_padding(str):
    if (len(str) % 4 != 0):
        padding_needed = 4 - (len(str) % 4)
        str += '==='[:padding_needed]
    return str

def verify_jwt(token):
    token_parts = token.split('.')
    encoded_header, encoded_payload, encoded_signature = token_parts
    
    header_bytes = base64.urlsafe_b64decode(add_padding(encoded_header))
    payload_bytes = base64.urlsafe_b64decode(add_padding(encoded_payload))

    header = header_bytes.decode('utf-8')
    payload = payload_bytes.decode('utf-8')

    verification_token = construct_jwt(header, payload)
    verification_parts = verification_token.split('.')
    verify_header, verify_payload, verify_signature = verification_parts

    if(verify_signature == encoded_signature): return True
    else: return False