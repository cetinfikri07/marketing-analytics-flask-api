from sqlalchemy.ext.declarative import DeclarativeMeta
from decimal import Decimal
import json

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def flatten_list(lst):
    result = []
    for i in lst:
        if isinstance(i,list):
            result.extend(flatten_list(i))
        else:
            result.append(i)

    return result
