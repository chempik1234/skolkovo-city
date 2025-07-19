import uuid

from translation import *


def remove_newline_escapes(text: str) -> str:
    return text.replace("\\n", "\n")


def get_logging_extra(user_id) -> dict:
    request_id = str(uuid.uuid4())
    return {"request_id": request_id, "user_id": user_id}
