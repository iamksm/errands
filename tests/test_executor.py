import hashlib
import inspect
from unittest import TestCase, mock

from errands import PROJECT_ERRANDS
from errands.config import ErrandsConfig
from errands.executor import (
    WORKERS,
    BaseErrandsExecutor,
    LongErrandsExecutor,
    MediumErrandsExecutor,
    ShortErrandsExecutor,
    errand,
    perf_counter,
    sleep,
)
from errands.queues import ErrandException

BASE_DIR = "tests/dummy_project/"


@mock.patch("errands.executor.sleep")
class TestBaseErrandsExecutor(TestCase):
    def setUp(self) -> None:
        ErrandsConfig(BASE_DIR)
        return super().setUp()

    @mock.patch("errands.executor.LOGGER")
    def test_spin_up_queue_errands(self, mock_sleep, mock_logger):
        exec = BaseErrandsExecutor("MEDIUM", False)
        exec.loop = False
        exec.spin_up_queue_errands()
        mock_logger.info.call_count == 3
        mock_logger.warning.call_count == 1

    def test_spin_up_queue_errands_with_error(self, mock_sleep):
        exec = BaseErrandsExecutor("MEDIUM", False)
        exec.loop = False

        class MyMock(mock.Mock):
            def __name__(self):
                return "mock_func"

        errand = mock.Mock()
        mock_func = MyMock()
        errand.callable = mock_func
        mock_func.side_effect = Exception("Error imehappen")
        exec.errands_to_run = [errand]

        with self.assertLogs(level="ERROR") as logs:
            exec.spin_up_queue_errands()
            self.assertEqual(len(logs.output), 1)

    def test_execute_errand(self, mock_sleep):
        class MyMock(mock.Mock):
            def __name__(self):
                return "mock_func"

        mock_errand = mock.Mock()
        mock_errand.callable = MyMock()

        base_errand = BaseErrandsExecutor("MEDIUM", False)
        base_errand.loop = False
        base_errand.execute_errand(mock_errand)

        mock_errand.callable.assert_called_once()
        mock_errand._get_next_run.assert_called_once()


@mock.patch.object(ShortErrandsExecutor, "spin_up_queue_errands")
class TestShortErrandsExecutor(TestCase):
    def setUp(self) -> None:
        ErrandsConfig(BASE_DIR)
        return super().setUp()

    def test_initialization(self, mock_queue_spin_up):
        exec = ShortErrandsExecutor()

        self.assertEqual(exec.errand_type, "SHORT")
        self.assertEqual(
            exec.errands_to_run[0],
            tuple(PROJECT_ERRANDS.errands["SHORT"].values())[0],
        )
        self.assertEqual(exec.workers, WORKERS.get("SHORT"))


@mock.patch.object(MediumErrandsExecutor, "spin_up_queue_errands")
class TestMediumErrandsExecutor(TestCase):
    def setUp(self) -> None:
        ErrandsConfig(BASE_DIR)
        return super().setUp()

    def test_initialization(self, mock_queue_spin_up):
        exec = MediumErrandsExecutor()

        self.assertEqual(exec.errand_type, "MEDIUM")
        self.assertEqual(
            exec.errands_to_run[0],
            tuple(PROJECT_ERRANDS.errands["MEDIUM"].values())[0],
        )
        self.assertEqual(exec.workers, WORKERS.get("MEDIUM"))


@mock.patch.object(LongErrandsExecutor, "spin_up_queue_errands")
class TestLongErrandsExecutor(TestCase):
    def setUp(self) -> None:
        ErrandsConfig(BASE_DIR)
        return super().setUp()

    def test_initialization(self, mock_queue_spin_up):
        exec = LongErrandsExecutor()

        self.assertEqual(exec.errand_type, "LONG")
        self.assertEqual(
            exec.errands_to_run[0],
            tuple(PROJECT_ERRANDS.errands["LONG"].values())[0],
        )
        self.assertEqual(exec.workers, WORKERS.get("LONG"))


class TestErrandDecorator(TestCase):
    def test_decorated_function_added_to_project_errands(self):
        def dummy_func():
            pass

        errand("*/1 * * * *")(dummy_func)

        errands = PROJECT_ERRANDS.errands["MEDIUM"].keys()
        func_source = inspect.getsource(dummy_func).encode("utf-8")
        function_hash = hashlib.sha256(func_source).hexdigest()
        self.assertIn(function_hash, errands)

    def test_decorated_function_executed_immediately(self):
        def dummy_func():
            nonlocal executed
            executed = True

        executed = False
        decorated_func = errand("*/1 * * * *")(dummy_func)
        decorated_func()

        self.assertTrue(executed)

    def test_delay_method_executes_immediately(self):
        def dummy_func():
            # Simulate a process execution that takes
            # a long time but we don't plan to wait for
            # it to finish, this would have stalled the whole
            # test suite if we had to wait for it to finish
            sleep(100)

        decorated_func = errand("*/1 * * * *")(dummy_func)

        with self.assertLogs(level="INFO") as logs:
            start = perf_counter()
            decorated_func.delay()
            end = perf_counter()

            total = round(end - start)

            # Assert that the function is run in the background
            self.assertLess(total, 1)

            self.assertEqual(len(logs.output), 1)
            log = "INFO:errands.executor:Errand running in the background process"
            self.assertEqual(log, logs.output[0])

    def test_errand_type_not_known(self):
        def dummy_func():
            pass

        with self.assertRaises(ErrandException):
            errand("*/1 * * * *", errand_type="UNKNOWN")(dummy_func)

    def test_invalid_cron_string(self):
        def dummy_func():
            pass

        with self.assertRaises(ErrandException):
            errand("invalid_cron_string")(dummy_func)

    def test_errand_object_created_with_correct_attributes(self):
        def dummy_func():
            pass

        errand("*/1 * * * *")(dummy_func)

        an_errand = tuple(PROJECT_ERRANDS.errands["MEDIUM"].values())[0]
        self.assertEqual(an_errand.errand_type, "MEDIUM")
        self.assertEqual(an_errand.cron_string, "*/1 * * * *")

    def test_errand_object_added_to_project_errands(self):
        def dummy_func():
            pass

        errand("*/1 * * * *")(dummy_func)

        funcs = PROJECT_ERRANDS.errands["MEDIUM"].keys()
        func_source = inspect.getsource(dummy_func).encode("utf-8")
        function_hash = hashlib.sha256(func_source).hexdigest()
        self.assertIn(function_hash, funcs)
