import logging
from datetime import datetime

import pytz
from croniter import croniter

LOGGER = logging.getLogger(__name__)
ALLOWED_ERRAND_QUEUES = ("SHORT", "MEDIUM", "LONG")


class ErrandException(Exception):
    """Exception raised for errors in the Errand class."""

    ...


class Errand:
    """
    Represents a job that needs to be executed at a specific time
    according to a cron schedule.

    Attributes:
        errand_type (str): The type of the errand (e.g., "SHORT", "MEDIUM", "LONG").
        cron_string (str): The cron string representing the schedule for the errand.
        tz (pytz.timezone): The timezone for the errand's schedule.
        callable (callable): The callable object associated with the errand.
        start (datetime): The start time for calculating the next run time.
        crontab (croniter): The croniter object used for calculating the next run time.
        next_run (datetime): The next run time for the errand.
        sleep (float): The time interval until the next run time.
    """

    def __init__(self, callable, errand_type, cron_string):
        """
        Initializes the Errand object with the provided
        callable, errand type, and cron string.

        Args:
            callable (callable): The callable object associated with the errand.
            errand_type (str): The type of the errand (e.g., "SHORT", "MEDIUM", "LONG").
            cron_string (str): The cron string representing the schedule for the errand.

        Raises:
            ErrandException: If the errand type is not known
                or the cron string is invalid.
        """
        if errand_type.upper() not in ALLOWED_ERRAND_QUEUES:
            raise ErrandException(
                f"Only use allowed errand type in CAPS {ALLOWED_ERRAND_QUEUES}"
            )

        if not croniter.is_valid(cron_string):
            link = "https://crontab.guru/"
            raise ErrandException(
                f"Invalid cron string, use {link} to countercheck it's validity"
            )

        self.errand_type = errand_type
        self.cron_string = cron_string
        self.tz = pytz.timezone("Africa/Nairobi")
        self.callable = callable
        self._get_next_run()

    def _get_next_run(self):
        """
        Calculates the next run time based on the current time and the cron schedule.
        """
        self.start = self.tz.localize(datetime.now())
        self.crontab = croniter(self.cron_string, self.start)
        self.next_run = self.crontab.get_next(datetime)
        self.sleep = (self.next_run - self.start).total_seconds()

    def __repr__(self) -> str:
        """
        Returns a string representation of the Errand object.

        Returns:
            str: A string representation of the Errand object.
        """
        return f"""
        ERRAND
            Callable: {self.callable}
            Errand Type: {self.errand_type}
            Cronstring: {self.cron_string}
            Next Run: {self.next_run})"""


class ProjectErrands:
    """
    A singleton class that manages different types of errands.

    Methods:
    - add_errand: Adds an errand to the appropriate errand queue based on its type.

    Fields:
    - short_errands: A dictionary to store short errands.
    - medium_errands: A dictionary to store medium errands.
    - long_errands: A dictionary to store long errands.
    - errands: A dictionary that maps errand types to their respective errand queues.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProjectErrands, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.short_errands = dict()
        self.medium_errands = dict()
        self.long_errands = dict()

        self.errands = {
            "SHORT": self.short_errands,
            "MEDIUM": self.medium_errands,
            "LONG": self.long_errands,
        }

    def add_errand(self, errand: Errand):
        """
        Adds an errand to the appropriate errand queue based on its type.

        Parameters:
        - errand: An instance of the Errand class representing the errand to be added.
        """
        errand_queue = self.errands.get(errand.errand_type, "MEDIUM")
        errand_queue[errand.callable] = errand

    def __repr__(self) -> str:
        """
        Returns a formatted string representation of the registered errands.

        Returns:
        - A string representing the registered errands.
        """
        short_errands = "\n ".join(str(e) for e in self.short_errands.values())
        medium_errands = "\n ".join(str(e) for e in self.medium_errands.values())
        long_errands = "\n ".join(str(e) for e in self.long_errands.values())

        return f"""
REGISTERED ERRANDS
    SHORT ERRANDS:
        {short_errands if short_errands else 'No short errands'}
    MEDIUM ERRANDS:
        {medium_errands if medium_errands else 'No medium errands'}
    LONG ERRANDS:
        {long_errands if long_errands else 'No long errands'}"""
