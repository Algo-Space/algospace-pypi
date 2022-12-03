'''
AlgoSpace: A platform for displaying algorithm achievements
'''

__version__ = 'v0.1.1'

from algospace.__main__ import run
from algospace.customer.service import login
from algospace.customer.service import info
from algospace.customer.service import fn
from algospace.customer.service import show_example
from algospace.customer.service import call
from algospace.customer.service import clear_storage


def __getattr__(algorithm_name: str):
    return fn(algorithm_name)
