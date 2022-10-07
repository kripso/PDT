import json
import os
import functools
import operator
from time import time
from DataExtractor import DataExtractor
from PostgresSchema import PostgresSchema
from PostgresClient import PostgresClient
from Tools import (
    create_postgres_connection,
    timer_function,
)
import csv

CONNECTION = create_postgres_connection()
UNIQUE_AUTHORS = {}
UNIQUE_TWEETS = {}
TWEET_REFERENCES = []

#
# authors
#
@timer_function("authors_block")
def authors_N_rows_parse(lines):
    block_entries = []

    for line in lines:
        _json_file = json.loads(line)
        author_id = _json_file.get("id")

        if author_id in UNIQUE_AUTHORS:
            continue

        UNIQUE_AUTHORS[author_id] = None
        block_entries.append(DataExtractor.generate_author_row(_json_file))

    PostgresClient.copy_authors(CONNECTION, block_entries)


@timer_function("authors_import")
def authors_N_rows_traverse(file_path: str, file_name: str):

    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_authors_table(cursor)

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []

        for index, line in enumerate(file):
            lines.append(line)

            if index % 1_000_000 == 0:
                authors_N_rows_parse(lines)
                lines = []

        authors_N_rows_parse(lines)


#
# Tweets
#
@timer_function("tweets_block")
def tweets_N_rows_parse(lines):
    tweet_entries = []
    block_left_over_authors = []

    for line in lines:
        _json_file = json.loads(line)
        tweet_id = _json_file.get("id")

        if tweet_id in UNIQUE_TWEETS:
            continue

        UNIQUE_TWEETS[tweet_id] = None
        tweet = DataExtractor.generate_tweet_row(_json_file)["tweet"]
        tweet_references = DataExtractor.generate_tweet_row(_json_file)[
            "tweet_references"
        ]
        author_id = tweet["author_id"]

        if author_id not in UNIQUE_AUTHORS:
            UNIQUE_AUTHORS[author_id] = None
            block_left_over_authors.append(
                DataExtractor.generate_author_row({"id": author_id})
            )

        tweet_entries.append(tweet)
        TWEET_REFERENCES.extend(tweet_references)

    PostgresClient.copy_authors(CONNECTION, block_left_over_authors)
    PostgresClient.copy_tweets(CONNECTION, tweet_entries)


@timer_function("tweets_import")
def tweets_N_rows_traverse(file_path: str, file_name: str):
    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_tweets_table(cursor)
        PostgresSchema.create_tweet_references_table(cursor)

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []
        for index, line in enumerate(file):
            lines.append(line)
            if index % 100_000 == 0:
                tweets_N_rows_parse(lines)
                lines = []
        tweets_N_rows_parse(lines)

    UNIQUE_AUTHORS.clear()
    tweet_references_parse()


@timer_function("tweet_references_block")
def tweet_references_parse():
    block_entries = []

    for index, tweet_reference in enumerate(TWEET_REFERENCES):
        parent_id = tweet_reference.get("parent_id")

        if parent_id in UNIQUE_TWEETS:
            block_entries.append(TWEET_REFERENCES.pop(index))

        if index % 100_000 == 0:
            PostgresClient.copy_tweet_references(CONNECTION, block_entries)
            block_entries = []

    PostgresClient.copy_tweet_references(CONNECTION, block_entries)
    TWEET_REFERENCES.clear()
    UNIQUE_TWEETS.clear()


# @timer_function("block")
# def links_N_rows_parse(lines):
#     block_entries = []

#     for line in lines:
#         _json_file = json.loads(line)
#         block_entries.append(DataExtractor.get_links_row(_json_file))

#     PostgresClient.copy_authors(
#         CONNECTION, filter(lambda x: x is not None, block_entries)
#     )


# @timer_function("block")
# def hashtags_N_rows_parse(lines):
#     block_entries = set()

#     for line in lines:
#         _json_file = json.loads(line)
#         block_entries.add(DataExtractor.get_hashtag(_json_file))

#     PostgresClient.copy_authors(CONNECTION, block_entries)

#
# Annotations
#
# @timer_function("block")
def annotations_N_rows_parse(lines):
    block_entries = []

    for line in lines:
        _json_file = json.loads(line)
        block_entries.extend(DataExtractor.get_annotations_row(_json_file))

    PostgresClient.copy_annotations(CONNECTION, block_entries)


# @timer_function("tweets_import")
def annotations_N_rows_traverse(file_path: str, file_name: str):
    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_annotations_table(cursor)

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []
        for index, line in enumerate(file):
            lines.append(line)
            if index % 100_000 == 0:
                annotations_N_rows_parse(lines)
                lines = []
        annotations_N_rows_parse(lines)


#
# Links
#
# @timer_function("block")
def links_N_rows_parse(lines):
    block_entries = []

    for line in lines:
        _json_file = json.loads(line)
        block_entries.extend(DataExtractor.get_links_row(_json_file))

    PostgresClient.copy_links(
        CONNECTION, filter(lambda x: x is not None, block_entries)
    )


# @timer_function("tweets_import")
def links_N_rows_traverse(file_path: str, file_name: str):
    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_links_table(cursor)

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []
        for index, line in enumerate(file):
            lines.append(line)
            if index % 100_000 == 0:
                links_N_rows_parse(lines)
                lines = []
        links_N_rows_parse(lines)


def obal(lines):
    @timer_function("N_rows_block")
    def N_rows_parse(lines):
        block_entries1 = []
        block_entries2 = []

        for line in lines:
            _json_file = json.loads(line)
            block_entries1.extend(DataExtractor.get_links_row(_json_file))
            block_entries2.extend(DataExtractor.get_annotations_row(_json_file))

        PostgresClient.copy_links(
            CONNECTION, filter(lambda x: x is not None, block_entries1)
        )
        PostgresClient.copy_annotations(CONNECTION, block_entries2)

    N_rows_parse(lines)


@timer_function("N_rows_import")
def N_rows_traverse(file_path: str, file_name: str):
    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_annotations_table(cursor)
        PostgresSchema.create_links_table(cursor)

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []
        for index, line in enumerate(file):
            lines.append(line)
            if index % 1_000_000 == 0:
                obal(lines)
                lines = []

    obal(lines)


import multiprocessing as mp
import psutil


@timer_function("paralel_import")
def paralel_import(file_path: str, file_name: str):
    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_annotations_table(cursor)
        PostgresSchema.create_links_table(cursor)

    procs = list()

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []
        for index, line in enumerate(file):
            lines.append(line)
            if index % 1_000_000 == 0:
                p = mp.Process(target=obal, kwargs={"lines": lines})
                p.start()
                procs.append(p)
                lines = []
    p = mp.Process(target=obal, kwargs={"lines": lines})
    p.start()
    procs.append(p)
    for p in procs:
        p.join()
        # print("joined")


def non_paralel_import():
    N_rows_traverse(
        "C:/Users/Krips/Documents/Programming/PDT/",
        "conversations.jsonl",
    )


if __name__ == "__main__":
    # authors_N_rows_traverse(
    #     "C:/Users/Krips/Documents/Programming/PDT/", "authors.jsonl"
    # )

    # tweets_N_rows_traverse(
    #     "C:/Users/Krips/Documents/Programming/PDT/",
    #     "conversations.jsonl",
    # )

    non_paralel_import()
    # paralel_import(
    #     "C:/Users/Krips/Documents/Programming/PDT/",
    #     "conversations.jsonl",
    # )
