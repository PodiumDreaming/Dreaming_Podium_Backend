from sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import pymysql

Remote = os.getenv("MariaDB")
db_url = f"mysql+pymysql://admin:jeongmh0902@{Remote}:3306/MariaDB?charset=utf8mb4"
# db_url = "mysql+pymysql://root:jeongmh0902@localhost:3306/dptest?charset=utf8mb4"

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()