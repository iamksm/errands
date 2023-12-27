import unittest
from unittest.mock import MagicMock, Mock

from errands.queues import Errand, ErrandException, ProjectErrands


class TestErrand(unittest.TestCase):
    def test_init_errand(self):
        callable_mock = MagicMock()
        errand = Errand(callable_mock, "SHORT", "* * * * *")
        self.assertEqual(errand.callable, callable_mock)
        self.assertEqual(errand.errand_type, "SHORT")
        self.assertEqual(errand.cron_string, "* * * * *")

    def test_calculate_next_run(self):
        callable_mock = MagicMock()
        errand = Errand(callable_mock, "SHORT", "* * * * *")
        errand._get_next_run()
        self.assertIsNotNone(errand.next_run)

    def test_string_representation(self):
        callable_mock = MagicMock()
        errand = Errand(callable_mock, "SHORT", "* * * * *")
        string_repr = repr(errand)
        self.assertIn("ERRAND", string_repr)
        self.assertIn("Callable", string_repr)
        self.assertIn("Errand Type", string_repr)
        self.assertIn("Cronstring", string_repr)
        self.assertIn("Next Run", string_repr)

    def test_invalid_errand_type(self):
        callable_mock = MagicMock()
        with self.assertRaises(ErrandException):
            Errand(callable_mock, "INVALID", "* * * * *")

    def test_invalid_cron_string(self):
        callable_mock = MagicMock()
        with self.assertRaises(ErrandException):
            Errand(callable_mock, "SHORT", "invalid_cron_string")


class TestProjectErrands(unittest.TestCase):
    def test_add_short_errand(self):
        def dummy_func():
            pass

        errand = Errand(dummy_func, "SHORT", "* * * * *")
        project_errands = ProjectErrands()
        project_errands.add_errand(errand)
        self.assertIn(errand, project_errands.short_errands.values())

    def test_add_medium_errand(self):
        def dummy_func():
            pass

        errand = Errand(dummy_func, "MEDIUM", "* * * * *")
        project_errands = ProjectErrands()
        project_errands.add_errand(errand)
        self.assertIn(errand, project_errands.medium_errands.values())

    def test_add_long_errand(self):
        def dummy_func():
            pass

        errand = Errand(dummy_func, "LONG", "* * * * *")
        project_errands = ProjectErrands()
        project_errands.add_errand(errand)
        self.assertIn(errand, project_errands.long_errands.values())

    def test_add_errand_overwrite_existing(self):
        def dummy_func():
            pass

        errand1 = Errand(dummy_func, "SHORT", "* * * * *")
        errand2 = Errand(dummy_func, "SHORT", "* * * * *")

        project_errands = ProjectErrands()
        project_errands.add_errand(errand1)
        project_errands.add_errand(errand2)

        # Check if the second errand overwrites the first errand
        self.assertNotIn(errand1, tuple(project_errands.short_errands.values()))
        self.assertIn(errand2, tuple(project_errands.short_errands.values()))
