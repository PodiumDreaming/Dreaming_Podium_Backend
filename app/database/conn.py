from sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import config
import pymysql

RDS_Account = config.RDS_Account
Local_Account = config.Local_Account
Remote = config.Remote
# db_url = f"mysql+pymysql://admin:{RDS_Account}@{Remote}:3306/MariaDB?charset=utf8mb4"
db_url = f"mysql+pymysql://root:{Local_Account}@localhost:3306/dptest?charset=utf8mb4"

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()