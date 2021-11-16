from datetime import datetime, date, timezone
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, JSON, BLOB
from sqlalchemy.ext.mutable import MutableDict
# from sqlalchemy.orm import relationship

from .conn import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255))
    gender = Column(String(255))
    birthday = Column(Date, nullable=True, default=None)
    team = Column(String(255), nullable=True, default=None)
    field = Column(String(255), nullable=True, default=None)
    email = Column(String(255), nullable=True, default=None)
    register_date = Column(DateTime)
    acc_type = Column(String(255))
    password = Column(String(255))
    refresh_token = Column(String(255))


# training record
class TR(Base):
    __tablename__ = "Training"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), ForeignKey("users.user_id"))
    written = Column(Date, default=date.today())
    last_modified = Column(DateTime, default=datetime.now(tz=timezone.utc).astimezone())
    content = Column(MutableDict.as_mutable(JSON))
    feedback = Column(String(255), nullable=True)


# Conditioning record
class CR(Base):
    __tablename__ = "Conditioning"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), ForeignKey("users.user_id"))
    written = Column(Date, default=date.today())
    last_modified = Column(DateTime, default=datetime.now(tz=timezone.utc).astimezone())
    content = Column(MutableDict.as_mutable(JSON))


class image(Base):
    __tablename__ = "Images"

    id = Column(Integer, primary_key=True, index=True)
    img_name = Column(String(255))
    img_data = Column(BLOB)
