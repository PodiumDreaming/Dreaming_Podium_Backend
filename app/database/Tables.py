from datetime import datetime, date, timezone
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, JSON
from sqlalchemy.ext.mutable import MutableDict
# from sqlalchemy.orm import relationship

from .conn import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(255), primary_key=True, index=True)
    # email = Column(String(255), nullable=True, default=None)
    register_date = Column(DateTime)
    acc_type = Column(String(255))
    password = Column(String(255))
    # refresh_token = Column(String(255))


class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(256), ForeignKey("users.user_id"))
    name = Column(String(255))
    gender = Column(String(255))
    birthday = Column(Date, nullable=True, default=None)
    team = Column(String(255), nullable=True, default=None)
    field = Column(String(255), nullable=True, default=None)
    profile_image = Column(MutableDict.as_mutable(JSON), nullable=True, default=None)


# training record
class TR(Base):
    __tablename__ = "Training"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey("users.user_id"))
    written = Column(Date, default=date.today())
    last_modified = Column(DateTime, default=datetime.now(tz=timezone.utc).astimezone())
    content = Column(MutableDict.as_mutable(JSON))
    feedback = Column(String(255), nullable=True)


# Conditioning record
class CR(Base):
    __tablename__ = "Conditioning"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(255), ForeignKey("users.user_id"))
    written = Column(Date, default=date.today())
    last_modified = Column(DateTime, default=datetime.now(tz=timezone.utc).astimezone())
    content = Column(MutableDict.as_mutable(JSON))


class Objective(Base):
    __tablename__ = "Objective"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(256), ForeignKey("users.user_id"), primary_key=True)
    objectives = Column(String(128), nullable=True)
    requirements = Column(String(256), nullable=True)
    efforts = Column(String(256), nullable=True)
    routines = Column(String(256), nullable=True)
