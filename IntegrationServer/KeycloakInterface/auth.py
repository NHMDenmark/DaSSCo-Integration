from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt
import requests
import dotenv
import os

dotenv.load_dotenv()

KEYCLOAK_URL = os.getenv("keycloak_url")
ALGORITHMS = [os.getenv("keycloak_algorithm")]
KEYCLOAK_REALM = os.getenv("keycloak_realm")

# Public key for signature validation
jwks = requests.get(f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs").json()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth",
    tokenUrl=f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
)

def get_token_header(token: str):
    unverified_header = jwt.get_unverified_header(token)
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return key
    raise HTTPException(status_code=401, detail="Invalid token header")

def verify_token(token: str = Depends(oauth2_scheme)):

    client_ids = os.getenv("keycloak_authorized_client_ids")

    key = get_token_header(token)
    
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=ALGORITHMS,
            issuer=f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}",
            options={"verify_aud": False}
        )

        if payload.get("azp") not in client_ids:
            raise HTTPException(401, "Invalid client")

        return payload
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token")

# checks first if the user is authenticated, then checks if they have any of the required roles
def require_roles(*required_roles):
    def checker(user: dict = Depends(verify_token)):

        try:
            roles = user.get("realm_access", {}).get("roles", [])
        except Exception as e:
            print(e)
            raise HTTPException(status_code=401, detail="Invalid token")

        if not any(role in roles for role in required_roles):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )

        return user

    return checker
    
def get_new_token():
    """
    Request a new Keycloak access token using Client Credentials flow.
    """

    client_id = os.getenv("keycloak_id")
    client_secret = os.getenv("keycloak_secret")

    if not client_id or not client_secret:
        raise RuntimeError("Missing keycloak_client_id or keycloak_client_secret")

    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"

    try:
        response = requests.post(
            token_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            allow_redirects=False,
            timeout=10
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to obtain token from Keycloak: {response.text}"
            )

        token_data = response.json()
        return token_data["access_token"]

    except Exception as e:
        print("Error requesting new Keycloak token:", e)
        raise HTTPException(status_code=500, detail="Error requesting new Keycloak token")