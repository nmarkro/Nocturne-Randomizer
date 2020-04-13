import os

try:
    from sys import _MEIPASS
    RANDO_ROOT_PATH = _MEIPASS
except ImportError:
    RANDO_ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

DATA_PATH = os.path.join(RANDO_ROOT_PATH, 'data')
PATCHES_PATH = os.path.join(RANDO_ROOT_PATH, 'patches')