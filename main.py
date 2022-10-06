import json
import os

from DataExtractor import DataExtractor
from PostgresSchema import PostgresSchema
from PostgresClient import PostgresClient
from Tools import (
    create_postgres_connection,
    timer_function,
)

CONNECTION = create_postgres_connection()
UNIQUE_AUTHORS = {}
UNIQUE_TWEETS = {}


#
# authors
#
@timer_function("block")
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


@timer_function("import")
def authors_N_rows_traverse(file_path: str, file_name: str):

    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_authors_table(cursor)

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []

        for index, line in enumerate(file):
            lines.append(line)

            if index % 10_000 == 0:
                authors_N_rows_parse(lines)
                lines = []

        authors_N_rows_parse(lines)


#
# Tweets
#
@timer_function("block")
def tweets_N_rows_parse(lines):
    block_entries = []
    block_left_over_authors = []

    for line in lines:
        _json_file = json.loads(line)
        tweet_id = _json_file.get("id")

        if tweet_id in UNIQUE_TWEETS:
            continue

        UNIQUE_TWEETS[tweet_id] = None
        tweet = DataExtractor.generate_tweet_row(_json_file)
        author_id = tweet["author_id"]

        if author_id not in UNIQUE_AUTHORS:
            UNIQUE_AUTHORS[author_id] = None
            block_left_over_authors.append(
                DataExtractor.generate_author_row({"id": author_id})["tweet"]
            )

        block_entries.append(tweet)

    PostgresClient.copy_authors(CONNECTION, block_left_over_authors)
    PostgresClient.copy_tweets(CONNECTION, block_entries)


@timer_function("import")
def tweets_N_rows_traverse(file_path: str, file_name: str):
    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_tweets_table(cursor)

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []

        for index, line in enumerate(file):
            lines.append(line)
            if index % 10_000 == 0:
                tweets_N_rows_parse(lines)
                lines = []
        tweets_N_rows_parse(lines)


@timer_function("block")
def links_N_rows_parse(lines):
    block_entries = []

    for line in lines:
        _json_file = json.loads(line)
        block_entries.append(DataExtractor.get_links_row(_json_file))

    PostgresClient.copy_authors(
        CONNECTION, filter(lambda x: x is not None, block_entries)
    )


@timer_function("block")
def hashtags_N_rows_parse(lines):
    block_entries = set()

    for line in lines:
        _json_file = json.loads(line)
        block_entries.add(DataExtractor.get_hashtag(_json_file))

    PostgresClient.copy_authors(CONNECTION, block_entries)


if __name__ == "__main__":
    authors_N_rows_traverse(
        "C:/Users/Krips/Documents/Programming/PDT/", "authors.jsonl"
    )

    tweets_N_rows_traverse(
        "C:/Users/Krips/Documents/Programming/PDT/",
        "conversations.jsonl",
    )
