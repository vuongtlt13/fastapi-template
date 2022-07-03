import random
import string


def random_string(length: int, choices=string.ascii_letters + string.digits) -> str:
    return ''.join(random.choice(choices) for _ in range(length))
