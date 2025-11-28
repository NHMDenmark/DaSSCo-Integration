from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt
import requests
import dotenv
import os

dotenv.load_dotenv()

KEYCLOAK_URL = os.getenv("keycloak_realm")
ALGORITHMS = [os.getenv("keycloak_algorithm")]

# Public key for signature validation
jwks = requests.get(f"{KEYCLOAK_URL}/protocol/openid-connect/certs").json()

def get_token_header(token: str):
    unverified_header = jwt.get_unverified_header(token)
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return key
    raise HTTPException(status_code=401, detail="Invalid token header")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_URL}/protocol/openid-connect/auth",
    tokenUrl=f"{KEYCLOAK_URL}/protocol/openid-connect/token",
)

def verify_token(token: str = Depends(oauth2_scheme)):

    client_ids = os.getenv("keycloak_client_ids")

    key = get_token_header(token)
    
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=ALGORITHMS,
            issuer=f"{KEYCLOAK_URL}",
            options={"verify_aud": False}
        )

        if payload.get("azp") not in client_ids:
            raise HTTPException(401, "Invalid client")

        return payload
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token")