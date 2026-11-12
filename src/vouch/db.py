import os

import psycopg

from vouch.config import require_env


def connect() -> psycopg.Connection:
    env = os.environ
    return psycopg.connect(
        host=require_env("POSTGRES_HOST", env),
        port=require_env("POSTGRES_PORT", env),
        user=require_env("POSTGRES_USER", env),
        password=require_env("POSTGRES_PASSWORD", env),
        dbname=require_env("POSTGRES_DB", env),
    )
