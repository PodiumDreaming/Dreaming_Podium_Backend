from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from .config.config import SECRET_KEY, ALGORITHM


"""# Parse string data and convert into list.
def simple_parser(target: str):
    if target == "[]":
        return []
    target = target.replace('"', "")
    target = target.replace("'", "")
    if target.startswith("[") and target.endswith("]"):
        target = target.replace("[", '').replace("]", '')
        if target.find(","):
            target = target.replace(", ", ",")
            result = target.split(",")
            for elem in result:
                elem.strip()
                return result

    if target == "":
        result = []
    else:
        result = [target]
    return result


# Warning: This function is specifically made to work with several cases.
# This function is not for general case.
# target will normally be "[]" or "[{some: data}, {some: data}]"
def complex_parser(target: str):
    res = []
    target = target.strip()
    target = target.replace('"', "")
    target = target.replace("'", "")
    target = target.replace("}, {", "},{")
    target = target.replace("} ,{", "},{")
    target = target.replace(" , ", ",")
    while True:
        if target.startswith("[") and target.endswith("]"):
            target = target.lstrip("[").rstrip("]")
            target = target.strip()
            continue
        if target.startswith("{") and target.endswith("}"):
            target = target.lstrip("{").rstrip("}")
            target = target.strip()
            continue
        if target.endswith(","):
            target = target.rstrip(",")
            target = target.strip()
            continue
        if target.find("}.{"):
            l1 = target.split("},{")
            if len(l1) == 1 and l1[0] == "":
                return res
        else:
            target.find(",")
            l1 = target.split(",")
            if len(l1) == 1 and l1[0] == "":
                return res
        break

    for i in range(len(l1)):
        l1[i].strip()
        l1[i] = l1[i].replace(", ", ",")
        l1[i] = l1[i].replace(": ", ":")
        l2 = l1[i].split(',')
        keys = []
        values = []
        for elem in l2:
            elem = elem.strip()
            l3 = elem.split(":")
            keys.append(l3[0])
            values.append(l3[1])
        injury = dict(zip(keys, values))
        for k, v in injury.items():
            if injury[k] == "None":
                injury[k] = None
        res.append(injury)

    return res"""


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
