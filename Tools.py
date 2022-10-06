from typing import Any, Optional
import psycopg2
import time
from datetime import datetime
import os

# def import_timer_function(function):
#     def wrap_function(*args, **kwargs):
#         import_start_time = time.time()
#         result = function(*args, **kwargs)
#         import_end_time = time.time()
#         time_delta = import_end_time - import_start_time
#         print(f"import time: {int(time_delta/60)}:{int(time_delta % 60)}")
#         return result

#     return wrap_function


def timer_function(_type):
    def wrap_function(function):
        def timing_function(*args, **kwargs):
            import_start_time = time.time()
            result = function(*args, **kwargs)
            import_end_time = time.time()
            time_delta = divmod(import_end_time - import_start_time, 60)
            print("------------------------------------")
            print(f"time now: {datetime.now().isoformat()}")
            print(f"{_type} time: {int(time_delta[0])}:{int(time_delta[1])}")

            return result

        return timing_function

    return wrap_function


def create_postgres_connection():
    connection = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    connection.autocommit = True
    return connection


def clean_csv_value(value: Optional[Any]):
    return (
        str(value)
        .replace("\n", "\\n")
        .replace("\t", "\\t")
        .replace("\r", "\\r")
        .replace("\\", "\\\\")
        .replace("\x00", "")
    )
