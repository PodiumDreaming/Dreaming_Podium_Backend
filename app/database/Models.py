from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class User(BaseModel):
    """
    user_id: 유저 고유 ID
    email: 이메일 주소
    register_date: 가입일
    acc_type: 가입 유형
    refresh_token: access_token 만료전에 재발급에 사용되는 토큰
    """
    user_id: str
    # email: Optional[str] = None
    register_date: datetime
    acc_type: str

    class Config:
        orm_mode = True


class UserFull(User):
    password: str


class Profile(BaseModel):
    """
    name: 이름
    gender: 성별
    birthday: 생년월일
    team: 소속 (팀)
    field: 종목
    profile_image: 프로필 사진
    """
    user_id: str
    name: str
    gender: str
    birthday: Optional[date]
    team: Optional[str]
    field: Optional[str]
    profile_image: Optional[dict]


class Record(BaseModel):
    """
    user_id: 유저 고유 ID
    written: 작성일
    last_modified: 최근 수정일
    content: 내용
    """
    user_id: str
    written: date
    last_modified: Optional[datetime]
    content: Optional[dict]


class Training(Record):
    feedback: Optional[str]

    class Config:
        orm_mode = True


class Condition(Record):

    class Config:
        orm_mode = True


class Image(BaseModel):
    img_name: str
    url: str
    user_id: str
    written: date
    last_modified: Optional[datetime]

    class Config:
        orm_mode = True
