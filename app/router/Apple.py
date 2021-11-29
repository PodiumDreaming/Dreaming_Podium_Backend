from fastapi import APIRouter, Depends, HTTPException, status
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from jose import jwt
from datetime import datetime, timedelta, timezone
from ..config.config import SOCIAL_AUTH_APPLE_KEY_ID, SOCIAL_AUTH_APPLE_TEAM_ID, CLIENT_ID
from ..database import Models, crud
from ..database.conn import get_db
from ..util import create_api_token


router = APIRouter(
    tags=["Apple"],
    dependencies=[],
)


"""def get_client_secret():
    with open("./app/config/AuthKey_X2H4DX2778.p8", "rb") as fp:
        SOCIAL_AUTH_APPLE_PRIVATE_KEY = fp.read().decode()

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


def verify_user(identity_code: str):
    response = requests.post("https://appleid.apple.com/auth/keys")

    # public_keys = response.json().get("Keys")
    pass"""


# Register new user
def sign_in(data: dict, db):
    if 'user' in data:
        user_id = "AP" + data['user']
        try:
            # check if user is already registered.
            user = crud.read_user(db=db, user_id=user_id)
            if user is not None:
                return user.user_id, user.password

            reg_date = datetime.now(tz=timezone.utc).astimezone()
            acc_type = "APPLE"
            token = create_api_token(user_id)

            # Make user model.
            user_data = {
                "user_id": user_id,
                "register_date": reg_date,
                "acc_type": acc_type,
            }
            user_db = Models.UserFull(**user_data, password=token)
            crud.create_user(db=db, user=user_db)
            return user_id, token

        except SQLAlchemyError:
            return {"Error": "SQL operation failed."}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not identify user.")


@router.post("/create_user")
async def register(res: dict, db: Session = Depends(get_db)):
    """
    Login with Appel Account.\n
    :param res: Response you received from Apple server.\n
    :param db: This field is not required.\n
    :return:  \n
    """
    user_id, token = sign_in(data=res, db=db)

    """response = authorize(authorization_code=authorize_code)
    if response.get("error", None):
        print("Apple login auth failed.")
        print(response.get("error"))
        return {"Error": "Authentication failed."}

    id_token = response.get("id_token", None)

    if id_token:
        payload = jwt.decode(id_token, '')
        return sign_in(payload, db)
    else:
        return {"Error": "Could not receive user information."}"""

    return {"user_id": user_id, "API_Token": token}
