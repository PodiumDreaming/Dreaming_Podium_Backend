from fastapi import APIRouter, Depends, HTTPException, status
import requests
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta, timezone

from ..config.config import SOCIAL_AUTH_APPLE_KEY_ID, SOCIAL_AUTH_APPLE_TEAM_ID, SOCIAL_AUTH_APPLE_PRIVATE_KEY, \
    CLIENT_ID
from ..database import Models, crud
from ..database.conn import get_db


router = APIRouter(
    tags=["Apple"],
    dependencies=[],
)


def get_client_secret():
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
        algorithm='RS256',
        headers=headers
    )
    return client_secret


def authorize(access_token, client_secret=Depends(get_client_secret)):
    client_id = CLIENT_ID

    headers = {'content-type': "application/x-www-form-urlencoded"}
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': access_token,
        'grant_type': 'authorization_code',
        'redirect_uri': "",
    }

    res = requests.post('https://appleid.apple.com/auth/token', data=data, headers=headers)
    response = res.json()
    id_token = response.get("id_token", None)

    if id_token:
        payload = jwt.decode(id_token, '')
        if 'sub' in payload:
            user_id = payload['sub']
            return user_id


@router.post("/register")
async def register():
    return get_client_secret()
