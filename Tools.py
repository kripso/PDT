from typing import Any, Optional
import psycopg2
import time
from datetime import datetime
import os
import csv

# def import_timer_function(function):
#     def wrap_function(*args, **kwargs):
#         import_start_time = time.time()
#         result = function(*args, **kwargs)
#         import_end_time = time.time()
#         time_delta = import_end_time - import_start_time
#         print(f"import time: {int(time_delta/60)}:{int(time_delta % 60)}")
#         return result

#     return wrap_function
total_time_delta = 0
total_time = time.perf_counter()


def timer_function(_type):
    def _timer_function(function):
        def timing_function(*args, **kwargs):
            start = time.perf_counter()
            result = function(*args, **kwargs)
            end = time.perf_counter()
            block_time_delta = end - start

            global total_time_delta
            global total_time

            total_time_delta = time.perf_counter() - total_time
            block_min, block_sec = divmod(block_time_delta, 60)
            import_min, import_sec = divmod(total_time_delta, 60)

            _time_now = time.strftime("%Y-%m-%dT%H:%MZ")
            _import_time = f"{int(import_min)}:{int(import_sec)}"
            _block_time = f"{int(block_min)}:{int(block_sec)}"

            print(
                _type,
                # time.strftime("%Y-%m-%dT%H:%MZ;")
                # + f"{int(import_min)}:{int(import_sec)}"
                # + f";{int(block_min)}:{int(block_sec)}",
                flush=True,
            )

            # with open("./docs/timer.csv", "a", encoding="UTF8", newline="") as f:
            #     writer = csv.writer(f, delimiter=";")

            #     # write the data
            #     writer.writerow((_time_now, _import_time, _block_time))
            return result

        return timing_function

    return _timer_function


def create_postgres_connection():
    connection = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    # connection.autocommit = True
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
