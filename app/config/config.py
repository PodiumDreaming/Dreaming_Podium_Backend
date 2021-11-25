import os

# KAKAO API
kakao_client = "6d1ba54d793cd90f64f3a4e84bbea36e"
callback_url = "http://localhost:8000/kakao/callback"

# APPLE API
SOCIAL_AUTH_APPLE_KEY_ID = os.getenv("SOCIAL_AUTH_APPLE_KEY_ID")
SOCIAL_AUTH_APPLE_TEAM_ID = os.getenv("SOCIAL_AUTH_APPLE_TEAM_ID")
CLIENT_ID = os.getenv("APPLE_CLIENT_ID")

# AWS RDS CONNECTION
Remote = os.getenv("MariaDB")
RDS_Account = os.getenv("RDS_Account")
Local_Account = os.getenv("Local_Account")

# AWS S3 CONNECTION
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET")
