import random
import string

import pytest

RAND_STRING_LENGTH = 10
CHARACTERS_FOR_GENERATIONS = string.ascii_letters + string.digits


@pytest.fixture
def random_string():
    the_random_string = ''
    for _ in range(RAND_STRING_LENGTH):
        the_random_string += random.choice(CHARACTERS_FOR_GENERATIONS)
    return the_random_string
