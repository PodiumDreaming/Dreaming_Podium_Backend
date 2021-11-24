# parse and reform target string into list.
from datetime import datetime


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

    return res


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