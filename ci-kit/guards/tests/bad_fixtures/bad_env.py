"""Deliberately-bad fixture for guard_env_var_in_config. Not imported anywhere.

Reads an env var outside the config registry, which must fail the guard.
"""
import os

SOME_SETTING = os.environ.get("SOME_SETTING", "default")
