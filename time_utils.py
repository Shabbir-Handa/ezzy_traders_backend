from datetime import datetime
from zoneinfo import ZoneInfo


IST_TZ_NAME = "Asia/Kolkata"


def get_ist_timezone():
    return ZoneInfo(IST_TZ_NAME)


def now_ist() -> datetime:
    tz = get_ist_timezone()
    if tz is None:
        return datetime.now()
    # Return naive IST wall time to align with DB columns without timezone
    return datetime.now(tz).replace(tzinfo=None)


def format_datetime_ist(value: datetime) -> str:
    tz = get_ist_timezone()
    if tz is None:
        return value.strftime("%d-%m-%Y.%H:%M:%S")
    if value.tzinfo is None:
        value = value.replace(tzinfo=tz)
    else:
        value = value.astimezone(tz)
    return value.strftime("%d-%m-%Y.%H:%M:%S")


