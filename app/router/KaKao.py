from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import requests
from sqlalchemy.orm import Session
from datetime import datetime

from ..config.config import kakao_client, callback_url
from ..database import Models, crud
from ..database.conn import get_db
from .Account import get_password_hash

router = APIRouter(
    tags=["KaKao"],
    dependencies=[],
)


def kakao_signin(info, refresh_token, db):
    kakao_account = info.get("kakao_account")
    profile = kakao_account.get("profile")

    """
    Check if user already exists in database.
    If so, then create user instance with the information in database.
    Otherwise, create new record in database and make user instance with that information.
    Then create a jwt token base on the user instance.
    """

    user_id = str(info.get("id", None))
    name = profile.get("nickname", None)
    gender = kakao_account.get("gender", None)
    email = kakao_account.get("email", None)
    reg_date = datetime.now().astimezone()
    acc_type = "KAKAO"

    password = get_password_hash(user_id)

    data = {
        "user_id": user_id,
        "name": name,
        "gender": gender,
        "email": email,
        "register_date": reg_date,
        "acc_type": acc_type,
    }
    user = Models.User(**data)
    user_db = Models.UserFull(**data, password=password, refresh_token=refresh_token)
    crud.create_user(db=db, user=user_db)
    return user


@router.get("/kakao/me", response_model=Models.User)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    current_user = crud.read_user(db, user_id)
    if current_user is None:
        raise HTTPException(status_code=404, detail="Could not find user")
    return current_user


@router.delete("/kakao/quit")
async def deleter_user(user_id: str, db: Session = Depends(get_db)):
    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="Could not find user")
    else:
        return {"status": "200"}


@router.get("/kakao/login")
async def kakao_login():
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={kakao_client}&redirect_uri={callback_url}&response_type=code"
    return RedirectResponse(auth_url)


@router.get("/kakao/callback")
async def get_token(code):
    if code:
        token_url = f"https://kauth.kakao.com/oauth/token?" \
                    f"grant_type=authorization_code&client_id={kakao_client}&redirect_uri={callback_url}&code={code}"
        res = requests.post(token_url)
        res = res.json()
        return res
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to Authorization from Kakao",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/kakao/form")
async def get_info(tokens: dict, db: Session = Depends(get_db)):
    """
    :param tokens:
    {"access_token": access_token, "refresh_token": refresh_token"}
    :param db:
    DB connect session
    :return:
    """
    # get kakao profile info using access token
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("access_token")
    if access_token is not None:
        info_rq = requests.get("https://kapi.kakao.com/v2/user/me",
                               headers={"Authorization": f"Bearer {access_token}"})
        info = info_rq.json()
        return kakao_signin(info, refresh_token, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
