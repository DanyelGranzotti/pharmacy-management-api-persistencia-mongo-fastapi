from bson import ObjectId
from bson.errors import InvalidId

def validate_object_id(v: str) -> str:
    try:
        ObjectId(v)
        return v
    except InvalidId:
        raise ValueError('Invalid ObjectId format')
