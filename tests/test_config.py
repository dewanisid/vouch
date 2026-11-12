import pytest

from vouch.config import MissingConfigError, require_env


def test_returns_value_when_variable_is_set():
    env = {"DB_PASSWORD": "secret"}

    assert require_env("DB_PASSWORD", env) == "secret"


def test_raises_naming_the_variable_when_missing():
    with pytest.raises(MissingConfigError, match="DB_PASSWORD"):
        require_env("DB_PASSWORD", {})


def test_returns_the_requested_variable_when_several_are_set():
    env = {"DB_HOST": "localhost", "DB_PASSWORD": "secret"}

    assert require_env("DB_HOST", env) == "localhost"


def test_raises_when_variable_is_set_but_empty():
    with pytest.raises(MissingConfigError, match="DB_PASSWORD"):
        require_env("DB_PASSWORD", {"DB_PASSWORD": ""})
