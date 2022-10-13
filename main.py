import json
import os
from DataExtractor import DataExtractor
from PostgresSchema import PostgresSchema
from PostgresClient import PostgresClient
from Tools import (
    create_postgres_connection,
    timer_function,
)
import multiprocessing as mp


CONNECTION = create_postgres_connection()
UNIQUE_AUTHORS = set()
UNIQUE_TWEETS = set()
UNIQUE_ENTITIES = set()
UNIQUE_DOMAINS = set()
UNIQUE_HASHTAGS = set()
tag_id = 0


#
# Traverse funcitons
#
def authors_traverse(file_path: str, file_name: str):
    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        authors = []

        for line in file:
            _json_file = json.loads(line)
            author_id = _json_file.get("id")

            if author_id in UNIQUE_AUTHORS:
                continue

            UNIQUE_AUTHORS.add(author_id)
            authors.append(DataExtractor.generate_author_row(_json_file))

            if len(authors) > 10_000:
                PostgresClient.copy_authors(CONNECTION, authors)
                authors = []

    PostgresClient.copy_authors(CONNECTION, authors)


def tweets_traverse(file_path: str, file_name: str):

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        tweets = []
        authors = []
        for line in file:
            _json_file = json.loads(line)
            tweet_id = _json_file.get("id")

            if tweet_id in UNIQUE_TWEETS:
                continue

            UNIQUE_TWEETS.add(tweet_id)
            tweet = DataExtractor.generate_tweet_row(_json_file)
            tweets.append(tweet)

            author_id = tweet["author_id"]

            if author_id not in UNIQUE_AUTHORS:
                UNIQUE_AUTHORS.add(author_id)
                authors.append(DataExtractor.generate_author_row({"id": author_id}))

            if len(tweets) > 10_000:
                PostgresClient.copy_authors(CONNECTION, authors)
                PostgresClient.copy_tweets(CONNECTION, tweets)
                tweets = []
                authors = []

    PostgresClient.copy_authors(CONNECTION, authors)
    PostgresClient.copy_tweets(CONNECTION, tweets)
    UNIQUE_AUTHORS.clear()


def hashtags_traverse(file_path: str, file_name: str):
    global tag_id

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        hashtags = []
        tweet_hashtags = []
        for line in file:
            _json_file = json.loads(line)
            tweet_id = _json_file.get("id", r"\N")

            for hashtag in DataExtractor.get_hashtags(_json_file):
                if hashtag["tag"] in UNIQUE_HASHTAGS:
                    continue
                UNIQUE_HASHTAGS.add(hashtag["tag"])
                hashtag["id"] = tag_id
                hashtags.append(hashtag)
                tweet_hashtags.append({"tweet_id": tweet_id, "hashtag_id": tag_id})
                tag_id += 1

            if len(hashtags) > 10_000:
                PostgresClient.execute_hashtags(CONNECTION, hashtags)
                hashtags = []

            if len(tweet_hashtags) > 10_000:
                PostgresClient.copy_tweet_hashtags(CONNECTION, tweet_hashtags)
                tweet_hashtags = []

    PostgresClient.execute_hashtags(CONNECTION, hashtags)
    PostgresClient.copy_tweet_hashtags(CONNECTION, tweet_hashtags)
    UNIQUE_HASHTAGS.clear()


def context_entities_filter(context_entities):
    block_entries = []

    for context_entity in context_entities:
        context_entity_id = context_entity.get("id")

        if context_entity_id not in UNIQUE_ENTITIES:
            block_entries.append(context_entity)
            UNIQUE_ENTITIES.add(context_entity_id)

    return block_entries


def context_domains_filter(context_domains):
    block_entries = []

    for context_domain in context_domains:
        context_domain_id = context_domain.get("id")

        if context_domain_id not in UNIQUE_DOMAINS:
            block_entries.append(context_domain)
            UNIQUE_DOMAINS.add(context_domain_id)

    return block_entries


def context_items_import(file_path: str, file_name: str):

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        context_entities = []
        context_domains = []

        for line in file:
            _json_file = json.loads(line)

            context_entities.extend(
                context_entities_filter(DataExtractor.get_context_entities(_json_file))
            )
            context_domains.extend(
                context_domains_filter(DataExtractor.get_context_domains(_json_file))
            )
            if len(context_entities) > 10_000:
                PostgresClient.copy_context_entities(CONNECTION, context_entities)
                context_entities = []
            if len(context_domains) > 10_000:
                PostgresClient.copy_context_domains(CONNECTION, context_domains)
                context_domains = []

    PostgresClient.copy_context_entities(CONNECTION, context_entities)
    PostgresClient.copy_context_domains(CONNECTION, context_domains)
    UNIQUE_DOMAINS.clear()
    UNIQUE_ENTITIES.clear()


#
# Tweet references
#
def tweet_references_traverse(file_path: str, file_name: str, UNIQUE_TWEETS):
    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        block_entries = []
        
        for line in file: 
            for tweet_reference in DataExtractor.generate_tweet_references(json.loads(line)):
                parent_id = tweet_reference.get("parent_id")
                if parent_id in UNIQUE_TWEETS:
                    block_entries.append(tweet_reference)
                
            if len(block_entries) > 10_000:
                PostgresClient.copy_tweet_references(CONNECTION, block_entries)

    PostgresClient.copy_tweet_references(CONNECTION, block_entries)

#
# Context Annotations
#
def context_annotations_traverse(file_path: str, file_name: str):

    with open(os.path.join(file_path, file_name), encoding="utf-8") as file:
        context_annotations = []

        for line in file:
            _json_file = json.loads(line)
            context_annotations.extend(DataExtractor.get_context_annotations_row(_json_file))
            if len(context_annotations) > 10_000:
                PostgresClient.copy_context_annotations(CONNECTION, context_annotations)
                context_annotations = []

        PostgresClient.copy_context_annotations(CONNECTION, context_annotations)


#
# paralel_import
#
def N_rows_import(lines):
    links = []
    annotations = []

    for line in lines:
        _json_file = json.loads(line)
        links.extend(DataExtractor.get_links_row(_json_file))
        annotations.extend(DataExtractor.get_annotations_row(_json_file))

    PostgresClient.copy_links(filter(lambda x: x is not None, links))
    PostgresClient.copy_annotations(CONNECTION, annotations)(annotations)


def paralel_import(file_path: str):
    _kwargs = {"file_path": file_path, "file_name": "conversations.jsonl"}

    procs = list()

    p = mp.Process(target=context_items_import,kwargs=_kwargs)
    p.start()
    procs.append(p)

    authors_traverse(file_path, "authors.jsonl")
    tweets_traverse(file_path, "conversations.jsonl")

    p = mp.Process(target=context_annotations_traverse,kwargs=_kwargs)
    p.start()
    procs.append(p)

    p = mp.Process(target=hashtags_traverse,kwargs=_kwargs)
    p.start()
    procs.append(p)

    __kwargs = _kwargs.copy()
    __kwargs["UNIQUE_TWEETS"] = UNIQUE_TWEETS

    p = mp.Process(target=tweet_references_traverse,kwargs=__kwargs)
    p.start()
    procs.append(p)

    with open(os.path.join(file_path, "conversations.jsonl"), encoding="utf-8") as file:
        lines = []
        for index, line in enumerate(file):
            lines.append(line)
            if index % 1_000_000 == 0:
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
    with CONNECTION.cursor() as cursor:
        PostgresSchema.create_authors_table(cursor)
        PostgresSchema.create_tweets_table(cursor)
        PostgresSchema.create_context_annotations_table(cursor)
        PostgresSchema.create_hashtags_table(cursor)
        PostgresSchema.create_tweet_hashtags_table(cursor)
        PostgresSchema.create_context_domains_table(cursor)
        PostgresSchema.create_context_entities_table(cursor)
        PostgresSchema.create_annotations_table(cursor)
        PostgresSchema.create_links_table(cursor)
        PostgresSchema.create_tweet_references_table(cursor)

    paralel_import("C:/Users/Krips/Documents/Programming/PDT/")

    CONNECTION.commit()
    # 16:09
