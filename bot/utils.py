import datetime
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


def get_seconds_till_next_weather() -> int:
    target_times = [9, 13, 17, 21]

    now = datetime.datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    current_second = now.second

    next_time = None
    if current_hour >= 21:
        tomorrow = now + datetime.timedelta(days=1)
        next_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0)
    else:  # so today is not over
        for hour in target_times:
            if current_hour < hour or (current_hour == hour and current_minute == 0 and current_second == 0):
                next_time = datetime.datetime(now.year, now.month, now.day, hour, 0, 0)
                break

    # whatever the reason we can wait for the next day
    if next_time is None:
        tomorrow = now + datetime.timedelta(days=1)
        next_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0)

    time_difference = next_time - now
    return int(time_difference.total_seconds())
