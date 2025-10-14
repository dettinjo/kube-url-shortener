import hashlib
import string
import random
import regex
import base64
import requests
import json
import os
from flask import request, abort, current_app
from werkzeug.exceptions import HTTPException

BASE62_ALPHABET = string.digits + string.ascii_letters

def base62_encode(num):
    """Encodes an integer into a Base62 string."""
    if num == 0:
        return BASE62_ALPHABET[0]
    
    encoded = []
    base = len(BASE62_ALPHABET)  

    while num:
        num, remainder = divmod(num, base)
        encoded.append(BASE62_ALPHABET[remainder])

    return ''.join(reversed(encoded))

def generate_short_id(url, length=6):
    """Generates a unique short ID for a URL."""
    randomNum = ''.join(random.choices(BASE62_ALPHABET, k=8))
    hash_digest = hashlib.sha256((url + randomNum).encode()).hexdigest()
    num = int(hash_digest[:10], 16)  
    return base62_encode(num)[:length]

def regex_validation(url):
    """Check whether url follows valid structure"""
    #https://stackoverflow.com/questions/1856785/characters-allowed-in-a-url reference to the /^[A-Za-z0-9\-._~!$&'()*+,;=:@\/?]*$/ , which is a PCRE expression that matches valid, unescaped fragment from RFC 2234
    url_regex = r"^((?:http(s)?):\/\/)?(www\\.)?(?!\\.|\\-|www\\.)([a-zA-Z0-9_.-]+)(\.[A-Za-z]{2,})((\/)[A-Za-z0-9\\-–.__~#!$&'()*+,;=:@\/?]*)?$"
    if regex.match(url_regex, url):
        return 0
    return 1

def regex_validate_jwt_string(str):
    return regex.match("^[A-Za-z0-9_-]{2,}(\\.[A-Za-z0-9_-]{2,}){2}$", str)

def check_authentication():
    """checks & verifies authentication based on the provided access token. on successful verification, returns the user's info  
       NOTE: this method should only be invoked from within a flask route method"""
    try:
        authHeaderName = "Authorization"
        jwt = request.headers.get(authHeaderName)
        if not regex_validate_jwt_string(jwt):
            raise Exception("")
    
        token_json = {"token": jwt}
        
 
        # Determine if running in a containerized environment
        is_containerized = os.getenv("DOCKER_ENV") or os.getenv("KUBERNETES_SERVICE_HOST")

        # Get auth service host and port dynamically
        auth_service_host = os.getenv("AUTH_SERVICE_HOST", "auth-service" if is_containerized else "localhost")
        auth_service_port = os.getenv("AUTH_SERVICE_PORT", "8001")

        auth_service_url = f"http://{auth_service_host}:{auth_service_port}"

        # Pass token to auth service for verification
        resp = requests.post(f"{auth_service_url}/users/login",
                             headers={'Content-Type': 'application/json'},
                             json=token_json)
        
        # if the token is verified by auth. service
        if resp.status_code==200:
            # extract and return the user_id from the verified token's payload
            encodedPayload = jwt.split(".")[1]
            padding = "".rjust(4-(len(encodedPayload)%4),'=')
            decodedPayload=base64.urlsafe_b64decode(encodedPayload+padding).decode("utf-8")
            payload=json.loads(decodedPayload)  
            return payload
        else:
            abort(403, description="authentication failure: access token verification failed")
    except HTTPException:
        raise
    except Exception as e:
        abort(403, description="missing or bad access token")

    
    

