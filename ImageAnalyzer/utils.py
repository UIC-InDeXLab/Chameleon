import os


def assert_env_var_not_none(env_var_name):
    env_var_value = os.environ.get(env_var_name)
    if env_var_value is None:
        raise ValueError(f"The environment variable `{env_var_name}` is not set.")
    return env_var_value
