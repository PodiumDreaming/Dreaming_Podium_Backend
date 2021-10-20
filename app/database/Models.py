from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class User(BaseModel):
    """
    name: 이름
    gender: 성별
    birthday: 생년월일
    team: 소속 (팀)
    field: 종목
    email: 이메일 주소
    register_date: 가입일
    acc_type: 가입 유형
    refresh_token: access_token 만료전에 재발급에 사용되는 토큰
    """
    user_id: str
    name: str
    gender: str
    birthday: Optional[datetime] = None
    team: Optional[str] = None
    field: Optional[str] = None
    email: Optional[str] = None
    register_date: datetime
    acc_type: str

    class Config:
        orm_mode = True


class UserFull(User):
    password: str
    refresh_token: str


class Record(BaseModel):
    user_id: str
    date: datetime
    content: dict


class Training(Record):
    feedback: str

    class Config:
        orm_mode = True


class Condition(Record):

    class Config:
        orm_mode = True

