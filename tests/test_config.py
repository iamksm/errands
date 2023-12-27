from unittest import TestCase

from errands import PROJECT_ERRANDS
from errands.config import ErrandsConfig


class TestErrandsConfig(TestCase):
    def test_init_config(self):
        self.assertEqual(PROJECT_ERRANDS.short_errands, dict())
        self.assertEqual(PROJECT_ERRANDS.medium_errands, dict())
        self.assertEqual(PROJECT_ERRANDS.long_errands, dict())

        from tests.dummy_project.app.config_file import BASE_DIR

        ErrandsConfig(BASE_DIR)
        errand_mapping = {
            "SHORT": "subtract_two_numbers",
            "MEDIUM": "add_numbers",
            "LONG": "multiply_numbers",
        }

        for errand_type, errands in PROJECT_ERRANDS.errands.items():
            self.assertEqual(len(errands), 1)
            errand = tuple(errands.values())[0]
            func_name = errand.callable.__name__
            assert func_name == errand_mapping[errand_type]
