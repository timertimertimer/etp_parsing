import re
import time
from zoneinfo import ZoneInfo
from dateutil import parser
from datetime import datetime, timedelta, UTC, timezone
from typing import Optional

from .logger import logger


class InvalidFormatDateTime(Exception):
    pass


class InvalidTimezoneOffsetAbbreviation(Exception):
    pass


class DateTimeHelper:
    moscow_tz = ZoneInfo("Europe/Moscow")
    sql_time_format = "%Y-%m-%d %H:%M:%S"
    iso_time_format = "%Y-%m-%dT%H:%M:%S"

    @staticmethod
    def get_timezone_with_offset_from_moscow(offset: int) -> timezone:
        moscow_offset = timedelta(hours=3)
        total_offset = moscow_offset + timedelta(hours=offset)
        return timezone(total_offset, name=f"MSK+{offset}")

    @staticmethod
    def format_datetime(dt: datetime, return_format: str = sql_time_format) -> Optional[str]:
        if not isinstance(dt, datetime):
            return None
        return dt.strftime(return_format)

    @staticmethod
    def smart_parse(string: str, input_time_format: str | list = iso_time_format) -> Optional[datetime]:
        if not string:
            return None

        dt = None
        try:
            dt = parser.isoparse(string)
        except Exception:
            pass

        if isinstance(input_time_format, str):
            input_time_format = [input_time_format]
        possible_formats = [
            DateTimeHelper.sql_time_format,
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y",
        ] + input_time_format

        for fmt in possible_formats:
            if dt is None:
                try:
                    dt = datetime.strptime(string, fmt)
                    break
                except Exception:
                    try:
                        match = re.search(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", string)
                        if match:
                            dt = datetime.strptime(match.group(), fmt)
                            break

                        match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", string)
                        if match:
                            dt = datetime.strptime(match.group(), fmt)
                            break
                    except Exception:
                        pass
        if dt is None:
            error_message = f"Could not parse date from {string=}"
            logger.warning(error_message)

        return dt

    @staticmethod
    def compare(time_string_1: str, time_string_2: str, url: str) -> int:
        date_var1 = time.strptime(time_string_1, "%d.%m.%Y %H:%M")
        date_var2 = time.strptime(time_string_2, "%d.%m.%Y %H:%M")

        if date_var1 > date_var2:
            return 1
        elif date_var2 > date_var1:
            return 2
        else:
            logger.warning(f"{url} | ERROR WITH CHECK TIME WHAT IS BIGGER", exc_info=True)
            return 0

    @staticmethod
    def parse_time_period(time_string: str) -> Optional[datetime]:
        if not time_string:
            return None
        try:
            cleaned = str(time_string).strip("\n, -").replace("- ", "").replace("&nbsp;", "")
            return datetime.strptime(cleaned, "%d.%m.%Y %H:%M:%S")
        except Exception:
            return None


if __name__ == '__main__':
    print(DateTimeHelper.get_timezone_with_offset_from_moscow(2))
