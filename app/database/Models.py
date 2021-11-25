from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


class User(BaseModel):
    """
    user_id: 유저 고유 ID\n
    register_date: 가입일\n
    acc_type: 가입 유형\n
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
    user_id: 유저 고유 ID\n
    name: 이름\n
    gender: 성별\n
    birthday: 생년월일\n
    team: 소속 (팀)\n
    field: 종목\n
    profile_image: 프로필 사진 url\n
    """
    user_id: str
    name: str
    gender: str
    birthday: Optional[date]
    team: Optional[str]
    field: Optional[str]
    profile_image: Optional[list]


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


class Objectives(BaseModel):
    """
    user_id: 유저 고유 ID\n
    objectives: 목표\n
    requirements: 자질\n
    efforts: 노력\n
    routines: 루틴\n
    """
    user_id: str
    objectives: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    efforts: Optional[List[str]] = None
    routines: Optional[List[str]] = None

    class Config:
        orm_mode = True
