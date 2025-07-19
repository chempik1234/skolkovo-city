import uuid
from typing import Any

from translation import *


def remove_newline_escapes(text: str) -> str:
    return text.replace("\\n", "\n")


def get_logging_extra(user_id: Any) -> dict:
    request_id = str(uuid.uuid4())
    result = {"request_id": request_id}
    if user_id is not None:
        result["user_id"] = user_id
    return result
