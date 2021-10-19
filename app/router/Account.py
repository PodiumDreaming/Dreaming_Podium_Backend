from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from .. import Model
from ..config.config import kakao_client, callback_url
from ..database import crud
import requests

router = APIRouter(
    tags=["account"],
    dependencies=[],
)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "Evan": {
        "name": "Evan",
        "gender": "Male",
        "birthday": None,
        "user_id": "1",
        "team": None,
        "field": None,
        "acc_type": "DP",
        "email": None,
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
    "johndoe": {
        "name": "johndoe",
        "gender": "Male",
        "birthday": None,
        "user_id": "2",
        "team": None,
        "field": None,
        "acc_type": "DP",
        "email": "johndoe@example.com",
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_user(db, username: str):
    # db 연결
    # check if id in db
    if username in db:
        user_info = db[username]
        return Model.UserFull(**user_info)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def check_type(acc_type):
    if acc_type in ["DP", "KAKAO", "APPLE"]:
        return True
    else:
        return False


def kakao_signin(info):
    kakao_account = info.get("kakao_account")
    profile = kakao_account.get("profile")
    """
    Check if user already exists in database.
    If so, then create user instance with the information in database.
    Otherwise, create new record in database and make user instance with that information.
    Then create a jwt token base on the user instance.
    """

    """some db codes to check user data"""

    user_id = info.get("id", None)
    name = profile.get("nickname", None)
    gender = kakao_account.get("gender", None)
    email = kakao_account.get("email", None)
    reg_date = info.get("connected_at", None)
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
    user = Model.User(**data)
    user_db = Model.UserFull(**data, password=password)

    return {"access_token": user, "token_type": "bearer"}


@router.get("/me", response_model=Model.User)
async def login_test(current_user: Model.User = Depends(get_current_user)):
    return current_user


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/kakao/login")
async def kakao_login():
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={kakao_client}&redirect_uri={callback_url}&response_type=code"
    return RedirectResponse(auth_url)


@router.get("/kakao/callback", response_model=Token)
async def get_token(code):
    if code:
        token_url = f"https://kauth.kakao.com/oauth/token?" \
                    f"grant_type=authorization_code&client_id={kakao_client}&redirect_uri={callback_url}&code={code}"
        token_rq = requests.post(token_url)
        token = token_rq.json()
        access_token = token.get("access_token", None)
        if access_token is not None:
            info_rq = requests.get("https://kapi.kakao.com/v2/user/me",
                                   headers={"Authorization": f"Bearer {access_token}"})
            info = info_rq.json()
            return kakao_signin(info)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to Authorization from Kakao",
                headers={"WWW-Authenticate": "Bearer"},
            )


@router.get("/kakao/form")
async def get_info(info: dict = Body(...)):
    # get kakao profile info using access token
    pass
