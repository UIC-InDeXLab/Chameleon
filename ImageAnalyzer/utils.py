import os
import time
from functools import wraps


def assert_env_var_not_none(env_var_name):
    env_var_value = os.environ.get(env_var_name)
    if env_var_value is None:
        raise ValueError(f"The environment variable `{env_var_name}` is not set.")
    return env_var_value



def convert_list_to_dict(l: list) -> dict:
    q = {}
    if l is None:
        return q

    for i in l:
        k, v = i.split("=")
        q[k] = int(v)
    return q


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper
