import hashlib
import inspect
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
            Next Run: {self.next_run})
        """


class ProjectErrands:
    """
    A singleton class managing different types of errands.

    Methods:
        - add_errand: Adds an errand to the appropriate queue based on its type.

    Fields:
        - short_errands: Dictionary for storing short errands.
        - medium_errands: Dictionary for storing medium errands.
        - long_errands: Dictionary for storing long errands.
        - errands: Dictionary mapping errand types to their respective queues.
    """

    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProjectErrands, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not self._is_initialized:
            self.short_errands = dict()
            self.medium_errands = dict()
            self.long_errands = dict()

            self.errands = {
                "SHORT": self.short_errands,
                "MEDIUM": self.medium_errands,
                "LONG": self.long_errands,
            }

            self._is_initialized = True

    def generate_function_hash(self, func):
        """
        This method generates a unique hash for a given function.

        Parameters:
        func (function): The function for which the hash is to be generated.

        Returns:
        str: The hexadecimal representation of the hash.
        """

        # Serialize the function code and create a hash object using SHA-256
        func_source = inspect.getsource(func).encode("utf-8")
        function_hash = hashlib.sha256(func_source).hexdigest()

        return function_hash

    def add_errand(self, errand: Errand):
        """
        Adds an errand to the appropriate errand queue based on its type.

        Parameters:
        - errand: An instance of the Errand class representing the errand to be added.
        """
        errand_queue = self.errands.get(errand.errand_type, "MEDIUM")
        func_hash = self.generate_function_hash(errand.callable)
        errand_queue[func_hash] = errand

    def __repr__(self) -> str:  # pragma: no cover
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
