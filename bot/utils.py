import datetime
import uuid
from enum import EnumType
from typing import Any, Iterable

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


def split_text_for_telegram(string: str) -> list[str]:
    return [string[i: i + 4000] for i in range(0, len(string), 4000)]


def today_date() -> str:
    return datetime.date.today().strftime("%Y-%m-%d")


async def today_date_async() -> str:
    return today_date()


async def calculator_async(expression: str) -> str:
    try:
        return eval(expression)
    except Exception:
        return "invalid expression"
