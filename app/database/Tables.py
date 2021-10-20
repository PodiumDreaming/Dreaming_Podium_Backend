from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .conn import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255))
    gender = Column(String(255))
    birthday = Column(DateTime, nullable=True, default=None)
    team = Column(String(255), nullable=True, default=None)
    field = Column(String(255), nullable=True, default=None)
    email = Column(String(255), nullable=True, default=None)
    reg_date = Column(DateTime)
    acc_type = Column(String(255))
    password = Column(String(255))
    refresh_token = Column(String(255))
