from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from .config.config import SECRET_KEY, ALGORITHM


# Convert input data into datetime.date form.
# Works even if day is incorrect(Monday, Tuesday, etc), since the function detects today's date.
# e.g)) Fri Nov 26 2021 -> datetime(2021,11,26)
def convert_date(date):
    try:
        d = datetime.strptime(date, '%a %b %d %Y').date()
        detail = {"status": "200OK"}
    except KeyError:
        d = None
        detail = {"KeyError": "Check record has valid keys."}
    except (TypeError, ValueError):
        d = None
        detail = {"Type/Value Error": "Check if date has valid value or is in right format. Example: 'Fri Nov 05 2021'"}
    except Exception:
        d = None
        detail = {"Exception": "Could not handle data. Check if data is valid."}
    result = {"date": d, "detail": detail}
    return result


# create JWT for a user.
def create_api_token(user_id: str):
    headers = {
        'typ': "JWT",
        'alg': ALGORITHM
    }
    payload = {
        'iss': "Wright",
        'iat': datetime.now(tz=timezone.utc).astimezone(),
        'exp': datetime.now(tz=timezone.utc).astimezone() + timedelta(days=30),
        'sub': "API Token",
        "User": user_id
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, headers=headers, algorithm=ALGORITHM)

    return encoded_jwt


# verify token
def token_verification(token, user_id: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if user_id != payload.get("User", None):
            raise JWTError
    except jwt.ExpiredSignatureError:
        return False
    except JWTError:
        return False
    return True
