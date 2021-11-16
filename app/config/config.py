import os

kakao_client = "6d1ba54d793cd90f64f3a4e84bbea36e"
callback_url = "http://localhost:8000/kakao/callback"
Remote = os.getenv("MariaDB")
RDS_Account = os.getenv("RDS_Account")
Local_Account = os.getenv("Local_Account")