import os

from errands.config import ErrandsConfig

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


ERRANDS_CONFIG = ErrandsConfig(BASE_DIR)
