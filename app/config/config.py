import os

# KAKAO API
kakao_client = os.getenv("kakao_client")
callback_url = "http://localhost:8000/kakao/callback"

# AWS RDS CONNECTION
Remote = os.getenv("MariaDB")
RDS_Account = os.getenv("RDS_Account")
Local_Account = os.getenv("Local_Account")

# AWS S3 CONNECTION
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET")

# JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
