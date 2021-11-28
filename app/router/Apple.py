from fastapi import APIRouter, Depends
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from jose import jwt
from datetime import datetime, timedelta, timezone
from .Account import get_password_hash
from ..config.config import SOCIAL_AUTH_APPLE_KEY_ID, SOCIAL_AUTH_APPLE_TEAM_ID, CLIENT_ID
from ..database import Models, crud
from ..database.conn import get_db
from ..util import create_api_token


router = APIRouter(
    tags=["Apple"],
    dependencies=[],
)


def get_client_secret():
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
    pass


def sign_in(data: dict, db):
    if 'user' in data:
        user_id = "AP" + data['user']
        name = data.get("name")
        try:
            user = crud.read_user(db=db, user_id=user_id)
            if user is not None:
                return user.user_id

            reg_date = datetime.now(tz=timezone.utc).astimezone()
            acc_type = "APPLE"
            password = get_password_hash(user_id)

            user_data = {
                "user_id": user_id,
                "register_date": reg_date,
                "acc_type": acc_type,
            }
            user_db = Models.UserFull(**user_data, password=password)
            crud.create_user(db=db, user=user_db)
            return user_id

        except SQLAlchemyError:
            return {"Error": "SQL operation failed."}


@router.post("/create_user")
async def register(res: dict, db: Session = Depends(get_db)):
    """
    Login with Appel Account.\n
    :param res: Response you received from Apple server.\n
    :param db: This field is not required.\n
    :return:  \n
    """
    sample = {"authorizationCode": "c097a6a3f38d943c2b94f64078ee4b7c1.0.rrrtw.wERkLAu8QqxEOcnRpdnitQ",
              "authorizedScopes": [], "email": "sujinju0311@naver.com",
              "fullName": {"familyName": "park", "givenName": "jinju", "middleName": None,
                           "namePrefix": None, "nameSuffix": None, "nickname": None},
              "identityToken": "eyJraWQiOiJlWGF1bm1MIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJodHRwczovL2FwcGxlaWQuYXBwbGUuY29tIiwiYXVkIjoib3JnLndyaWdodGJ1aWxkIiwiZXhwIjoxNjM4MDYxMzY1LCJpYXQiOjE2Mzc5NzQ5NjUsInN1YiI6IjAwMTEzNi4zZThhODc0YTYxMjI0NmY3YjMzOTY3ZjM2YWViYTFmMS4wNDM4Iiwibm9uY2UiOiJiZTk5NTE4YjNhYjdhM2E2Zjg4NjFmMzM4MDc3OWZlMzJmMDc3MWVkMTFhZTc4ZTY3YWU3YmY4MmRhNzJhN2YwIiwiY19oYXNoIjoidVBWem5JRW9NNThEZXc4M2g2eWY0dyIsImVtYWlsIjoic3VqaW5qdTAzMTFAbmF2ZXIuY29tIiwiZW1haWxfdmVyaWZpZWQiOiJ0cnVlIiwiYXV0aF90aW1lIjoxNjM3OTc0OTY1LCJub25jZV9zdXBwb3J0ZWQiOnRydWUsInJlYWxfdXNlcl9zdGF0dXMiOjF9.zWK6US-xq8CBye4k4Qs_FsaEO2qNyObezyuJlPNxqTGQ3JGUQqUyrsfY_VUHH0RfhfuT2abaY4G0kOz8oI3GsTV8fth9078dE7OOFocvyYrjM2G2hzZgLFvHnrfk-y2y8XVs6GD-Nxovnhfn1rGzk34D5hvih13bty4r7gAHi34LHy7yFWXM-6SOF24DLh13LJXXCsZ0aRK9YSksTet93PjttdrQf6YknkcCL9cd6AETPJIc-FFnk_WDpMVeGY6A2RLD8J0T31-mjiHVLqx0kZuisd9EQ_OqfdokteDEXPJbkv1BgIFFEqUBmJ1W14EGRoneu4LOUXe6AxRy6HDFOA",
              "nonce": "8C.o3_.7QAyBd.kuBhNro.oFfdwO8MYH",
              "realUserStatus": 1,
              "state": None,
              "user": "001136.3e8a874a612246f7b33967f36aeba1f1.0438"}

    identity_code = res.get("identityToken")

    verify_user(identity_code)
    user_id = sign_in(data=res, db=db)
    token = create_api_token(user_id)
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


