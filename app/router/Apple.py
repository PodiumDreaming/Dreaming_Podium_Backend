from fastapi import APIRouter, Depends, HTTPException, status
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import jwt
from datetime import datetime, timedelta, timezone
from .Account import get_password_hash
from ..config.config import SOCIAL_AUTH_APPLE_KEY_ID, SOCIAL_AUTH_APPLE_TEAM_ID, CLIENT_ID
from ..database import Models, crud
from ..database.conn import get_db

router = APIRouter(
    tags=["Apple"],
    dependencies=[],
)


def get_client_secret():
    with open("./app/config/AuthKey_X2H4DX2778.p8", "rb") as fp:
        SOCIAL_AUTH_APPLE_PRIVATE_KEY = fp.read()

    headers = {
        'kid': SOCIAL_AUTH_APPLE_KEY_ID,
        'alg': "ES256"
    }

    payload = {
        'iss': SOCIAL_AUTH_APPLE_TEAM_ID,
        'iat': datetime.now(tz=timezone.utc).astimezone(),
        'exp': datetime.now(tz=timezone.utc).astimezone() + timedelta(days=180),
        'aud': 'https://appleid.apple.com',
        'sub': CLIENT_ID,
    }

    client_secret = jwt.encode(
        payload,
        SOCIAL_AUTH_APPLE_PRIVATE_KEY,
        algorithm='ES256',
        headers=headers
    )

    return client_secret


def verify_user(identity_code: str):
    public_codes = requests.post("https://appleid.apple.com/auth/keys")
    pass


def authorize(authorization_code, client_secret=Depends(get_client_secret)):
    client_id = CLIENT_ID

    headers = {'content-type': "application/x-www-form-urlencoded"}
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': "",
    }

    res = requests.post('https://appleid.apple.com/auth/token', data=data, headers=headers)
    response = res.json()
    return response


def sign_in(payload: dict, db):
    if 'sub' in payload:
        user_id = "AP" + payload['sub']

        try:
            user = crud.read_user(db=db, user_id=user_id)
            if user is not None:
                return user.user_id

            reg_date = datetime.now(tz=timezone.utc).astimezone()
            acc_type = "APPLE"
            password = get_password_hash(user_id)

            user_data = {
                "user_id": user_id,
                "name": None,
                "gender": None,
                # "email": email,
                "register_date": reg_date,
                "acc_type": acc_type,
            }
            user_db = Models.UserFull(**user_data, password=password)
            crud.create_user(db=db, user=user_db)
            return {"user_id": user_id}

        except SQLAlchemyError:
            return {"Error": "SQL operation failed."}


@router.post("/create_user")
async def register(codes: dict, db: Session = Depends(get_db)):
    """
    Login with Appel Account.\n
    :param codes: codes should be in dict form and include:\n
        "authorizationCode": code
        "identityToken": token
    :param db: \n
    :return:  \n
    """
    authorize_code = codes.get("authorizationCode")
    identity_code = codes.get("identityToken")

    verify_user(identity_code)

    response = authorize(authorization_code=authorize_code)
    if response.get("error", None):
        print("Apple login auth failed.")
        print(response.get("error"))
        return {"Error": "Authentication failed."}

    id_token = response.get("id_token", None)

    if id_token:
        payload = jwt.decode(id_token, '')
        return sign_in(payload, db)
    else:
        return {"Error": "Could not receive user information."}


@router.get("/jwt_test/")
async def encoding_test():
    return get_client_secret()
