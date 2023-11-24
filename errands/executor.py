import functools
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter, sleep

from errands import PROJECT_ERRANDS
from errands.queues import ALLOWED_ERRAND_QUEUES, Errand

TOTAL_WORKERS_TO_USE = os.cpu_count() // 2

PROCESSES = min(TOTAL_WORKERS_TO_USE, len(ALLOWED_ERRAND_QUEUES))

TOTAL_SPINABLE_THREADS = TOTAL_WORKERS_TO_USE + 4

LONG_ERRANDS_THREADS = round(TOTAL_SPINABLE_THREADS * 0.5)
MEDIUM_ERRANDS_THREADS = round(TOTAL_SPINABLE_THREADS * 0.3)
SHORT_ERRANDS_THREADS = round(TOTAL_SPINABLE_THREADS * 0.2)
WORKERS = {
    "SHORT": SHORT_ERRANDS_THREADS,
    "MEDIUM": MEDIUM_ERRANDS_THREADS,
    "LONG": LONG_ERRANDS_THREADS,
}
LOGGER = logging.getLogger(__name__)


def errand(cron_string: str, errand_type: str = "MEDIUM"):
    """
    A decorator that can be used to schedule and execute tasks at specific intervals.

    Args:
        cron_string (str): A string representing a cron expression that defines
            the schedule for the task.
        errand_type (str, optional): A string representing the type of the errand.
            This can be used to categorize and prioritize different types of tasks.

    Returns:
        function: A decorator function that can be used to decorate other functions.
            The decorated functions can be run in async using the `delay` method,
            or they can be executed immediately by calling the function directly.
    """

    def decorator(func):
        an_errand = Errand(func, errand_type, cron_string)
        PROJECT_ERRANDS.add_errand(an_errand)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        @functools.wraps(func)
        def delay(*args, **kwargs):
            return BaseErrandsExecutor.schedule_errand_now(
                errand_type, func, *args, **kwargs
            )

        wrapper.delay = delay
        return wrapper

    return decorator


class BaseErrandsExecutor:
    """
    Executes errands based on their type using a thread pool executor.

    Args:
        errand_type (str): The type of errands that the executor handles.

    Attributes:
        errand_type (str): The type of errands that the executor handles.
        errands_to_run (list): The list of errands to be executed.
        workers (int): The number of worker threads to be used.

    Example Usage:
        executor = BaseErrandsExecutor("MEDIUM")
        executor.spin_up_queue_errands()
    """

    def __init__(self, errand_type):
        self.errand_type = errand_type
        self.errands_to_run = PROJECT_ERRANDS.errands[self.errand_type].values()

        self.workers = WORKERS.get(self.errand_type)

    def spin_up_queue_errands(self):
        """
        Spins up a thread pool executor and executes the errands concurrently.
        """
        with ThreadPoolExecutor(
            max_workers=self.workers, thread_name_prefix=self.errand_type
        ) as executor:
            threads = executor.map(self.execute_errand, self.errands_to_run)
            while True:
                next(as_completed(threads))

    def execute_errand(self, errand):
        """
        Executes an individual errand by calling its associated function

        Args:
            errand (Errand): The errand to be executed.
        """
        func = errand.callable
        queue = f"[{self.errand_type} ERRANDS QUEUE]:"
        while True:
            LOGGER.info(f"{queue} {func.__name__} WILL RUN @{errand.next_run}")

            sleep(errand.sleep)

            LOGGER.info(f"{queue} RUNNING ERRAND {func.__name__}")

            try:
                start = perf_counter()
                func()
                end = perf_counter()
            except Exception as e:
                LOGGER.warning(e)

            errand._get_next_run()
            total = round(end - start, 4)

            LOGGER.info(f"DONE EXECUTING {func} - IN {total} seconds")

    @classmethod
    def schedule_errand_now(cls, func, *args, **kwargs):
        """
        Schedules an errand to be executed immediately by submitting it
        to a separate thread pool executor.

        Args:
            func (callable): The function to be executed as an errand.
            *args: Variable length argument list to be passed to the function.
            **kwargs: Arbitrary keyword arguments to be passed to the function.
        """
        with ThreadPoolExecutor(max_workers=1) as t_exec:
            thread = t_exec.submit(func, *args, **kwargs)
            thread.result()


class LongErrandsExecutor(BaseErrandsExecutor):
    def __init__(self) -> None:
        super().__init__("LONG")
        self.spin_up_queue_errands()


class MediumErrandsExecutor(BaseErrandsExecutor):
    def __init__(self) -> None:
        super().__init__("MEDIUM")
        self.spin_up_queue_errands()


class ShortErrandsExecutor(BaseErrandsExecutor):
    def __init__(self) -> None:
        super().__init__("SHORT")
        self.spin_up_queue_errands()
