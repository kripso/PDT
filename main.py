import json
import os
import functools
import operator
from pathlib import Path
from time import time
from DataExtractor import DataExtractor
from PostgresSchema import PostgresSchema
from PostgresClient import PostgresClient
from Tools import (
    create_postgres_connection,
    timer_function,
)
import csv
import multiprocessing as mp
import yaml
from yaml import CLoader as Loader

CONNECTION = create_postgres_connection()
UNIQUE_AUTHORS = {}
UNIQUE_TWEETS = {}
UNIQUE_ENTITIES = {}
UNIQUE_DOMAINS = {}

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
        tweet = DataExtractor.generate_tweet_row(_json_file)
        author_id = tweet["author_id"]

        if author_id not in UNIQUE_AUTHORS:
            UNIQUE_AUTHORS[author_id] = None
            block_left_over_authors.append(
                DataExtractor.generate_author_row({"id": author_id})
            )

        tweet_entries.append(tweet)

    PostgresClient.copy_authors(CONNECTION, block_left_over_authors)
    PostgresClient.copy_tweets(CONNECTION, tweet_entries)


@timer_function("tweets_import")
def tweets_N_rows_traverse(file_path: str, file_name: str):
    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_tweets_table(cursor)

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []
        for index, line in enumerate(file):
            lines.append(line)
            if index % 100_000 == 0:
                tweets_N_rows_parse(lines)
                lines = []
        tweets_N_rows_parse(lines)


#
# Tweet references
#
@timer_function("tweet_references_block")
def tweet_references_parse(lines):
    block_entries = []

    for tweet_reference in lines:
        parent_id = tweet_reference.get("parent_id")

        if parent_id in UNIQUE_TWEETS:
            block_entries.append(tweet_reference)

    PostgresClient.copy_tweet_references(CONNECTION, block_entries)


#
# Hashtags
#
@timer_function("hashtags_block")
def hashtags_parse(lines):
    block_entries = []

    for hashtag in lines:
        parent_id = hashtag.get("parent_id")

        # block_entries.append(hashtag)

    PostgresClient.copy_hashtags(CONNECTION, block_entries)


#
# Context Items
#
@timer_function("context_entities_block")
def context_entities_parse(context_entities):
    block_entries = []

    for context_entity in context_entities:
        context_entity_id = context_entity.get("id")

        if context_entity_id not in UNIQUE_ENTITIES:
            block_entries.append(context_entity)
            UNIQUE_ENTITIES[context_entity_id] = None

    PostgresClient.copy_context_entities(CONNECTION, block_entries)


@timer_function("context_domains_block")
def context_domains_parse(context_domains):
    block_entries = []

    for context_domain in context_domains:
        context_domain_id = context_domain.get("id")

        if context_domain_id not in UNIQUE_DOMAINS:
            block_entries.append(context_domain)
            UNIQUE_DOMAINS[context_domain_id] = None

    PostgresClient.copy_context_domains(CONNECTION, block_entries)


def context_items_import(file_path: str, file_name: str):
    @timer_function("context_items_import")
    def _context_items_import(file_path: str, file_name: str):
        with CONNECTION.cursor() as cursor:
            PostgresSchema.create_context_domains_table(cursor)
            PostgresSchema.create_context_entities_table(cursor)

        with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
            context_entities = []
            context_domains = []
            context_annotations = []

            for index, line in enumerate(file):
                _json_file = json.loads(line)

                context_entities.extend(DataExtractor.get_context_entities(_json_file))
                context_domains.extend(DataExtractor.get_context_domains(_json_file))
                context_annotations.extend(
                    DataExtractor.get_context_annotations_row(_json_file)
                )

                if index % 100_000 == 0:
                    context_entities_parse(context_entities)
                    context_domains_parse(context_domains)
                    PostgresClient.copy_context_domains(CONNECTION, context_annotations)

                    context_entities = []
                    context_domains = []
                    context_annotations = []

        context_entities_parse(context_entities)
        context_domains_parse(context_domains)
        PostgresClient.copy_context_domains(CONNECTION, context_annotations)
        UNIQUE_DOMAINS.clear()
        UNIQUE_ENTITIES.clear()

    _context_items_import(file_path, file_name)


#
# paralel_import
#
def N_rows_import(lines):
    @timer_function("N_rows_block")
    def _N_rows_import(lines):
        block_entries1 = []
        block_entries2 = []
        block_entries3 = []
        tweet_references = []

        for line in lines:
            _json_file = json.loads(line)
            block_entries1.extend(DataExtractor.get_links_row(_json_file))
            block_entries2.extend(DataExtractor.get_annotations_row(_json_file))
            block_entries3.extend(DataExtractor.get_hashtags(_json_file))
            tweet_references.extend(DataExtractor.generate_tweet_references(_json_file))

        PostgresClient.copy_links(
            CONNECTION, filter(lambda x: x is not None, block_entries1)
        )
        PostgresClient.copy_annotations(CONNECTION, block_entries2)
        PostgresClient.execute_hashtags(CONNECTION, block_entries3)
        # tweet_references_parse(tweet_references)

    _N_rows_import(lines)


@timer_function("paralel_import")
def paralel_import(file_path: str, file_name: str):
    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_annotations_table(cursor)
        PostgresSchema.create_links_table(cursor)
        PostgresSchema.create_hashtags_table(cursor)
        PostgresSchema.create_tweet_references_table(cursor)

    procs = list()

    p = mp.Process(
        target=context_items_import,
        kwargs={"file_path": file_path, "file_name": file_name},
    )
    p.start()
    procs.append(p)
    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        lines = []
        for index, line in enumerate(file):
            lines.append(line)
            if index % 100_000 == 0:
                p = mp.Process(target=N_rows_import, kwargs={"lines": lines})
                p.start()
                procs.append(p)
                lines = []

    p = mp.Process(target=N_rows_import, kwargs={"lines": lines})
    p.start()
    procs.append(p)
    for p in procs:
        p.join()


if __name__ == "__main__":
    # authors_N_rows_traverse(
    #     "C:/Users/Krips/Documents/Programming/PDT/", "authors.jsonl"
    # )

    # tweets_N_rows_traverse(
    #     "C:/Users/Krips/Documents/Programming/PDT/",
    #     "conversations.jsonl",
    # )

    UNIQUE_AUTHORS.clear()

    paralel_import(
        "C:/Users/Krips/Documents/Programming/PDT/",
        "conversations.jsonl",
    )
