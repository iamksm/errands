from functools import reduce
from operator import mul

from errands.executor import errand


@errand("*/1 * * * *", "SHORT")
def subtract_two_numbers():
    x = 40
    y = 20
    return x - y


@errand("*/1 * * * *", "MEDIUM")
def add_numbers():
    numbers = (x for x in range(100))
    the_sum = sum(numbers)
    return the_sum


@errand("*/1 * * * *", "LONG")
def multiply_numbers():
    numbers = (x for x in range(100))
    return reduce(mul, numbers)
