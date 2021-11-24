from sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import config
import boto3
from botocore.exceptions import ClientError
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


def get_s3():
    s3 = boto3.client('s3',
                      aws_access_key_id=config.AWS_ACCESS_KEY,
                      aws_secret_access_key=config.AWS_SECRET_KEY)
    try:
        yield s3
    except ClientError:
        print("s3 connection failed")
    except Exception as e:
        print(e)
