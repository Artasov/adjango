# utils/crontab.py
import re

from celery.schedules import crontab


class Crontab:

    @staticmethod
    def every(
        seconds=None,
        minutes=None,
        hours=None,
        days=None,
        monday=None,
        tuesday=None,
        wednesday=None,
        thursday=None,
        friday=None,
        saturday=None,
        sunday=None,
    ):
        """
        Generate crontab expressions for various time intervals
        """
        if seconds:
            return crontab(second=f"*/{seconds}")
        if minutes:
            return crontab(minute=f"*/{minutes}")
        if hours:
            return crontab(hour=f"*/{hours}")
        if days:
            return crontab(day_of_month=f"*/{days}")

        # For weekdays with time specification
        day_of_week = None
        time = None

        if monday:
            day_of_week = "1"
            time = Crontab._parse_time(monday)
        elif tuesday:
            day_of_week = "2"
            time = Crontab._parse_time(tuesday)
        elif wednesday:
            day_of_week = "3"
            time = Crontab._parse_time(wednesday)
        elif thursday:
            day_of_week = "4"
            time = Crontab._parse_time(thursday)
        elif friday:
            day_of_week = "5"
            time = Crontab._parse_time(friday)
        elif saturday:
            day_of_week = "6"
            time = Crontab._parse_time(saturday)
        elif sunday:
            day_of_week = "0"
            time = Crontab._parse_time(sunday)

        if day_of_week and time:
            hour, minute = time
            return crontab(day_of_week=day_of_week, hour=hour, minute=minute)

        raise ValueError("Invalid parameters for crontab generation")

    @staticmethod
    def _parse_time(time_str):
        """
        Helper method for parsing time strings in HH:MM format
        """
        match = re.match(r"(\d{1,2}):(\d{2})", time_str)
        if match:
            hour, minute = match.groups()
            return int(hour), int(minute)
        raise ValueError(f"Invalid time format: {time_str}")
