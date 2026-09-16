import itertools
import os

BACKENDS = os.getenv("UPSTREAMS", "http://backend-1:8000,http://backend-2:8000").split(",")

iterator = itertools.cycle(BACKENDS)

def get_next_backend():
    return next(iterator)