from Tools import timer_function
from PostgresClient import PostgresClient
from DataExtractor import DataExtractor
import multiprocessing as mp
import json
import os

UNIQUE_AUTHORS = set()
UNIQUE_TWEETS = set()
UNIQUE_ENTITIES = set()
UNIQUE_DOMAINS = set()
UNIQUE_HASHTAGS = dict()
PROCS = list()

DATA_PATH = "C:/Users/Krips/Documents/Programming/PDT/"
AUTHORS_FILE = "authors.jsonl"
TWEETS_FILE = "conversations.jsonl"

CLIENT = PostgresClient()

#
# Authors
#
def authors_import():
    @timer_function("Authors")
    def _authors_import():
        with open(os.path.join(DATA_PATH, AUTHORS_FILE), encoding="utf-8") as file:
            authors = []

            for line in file:
                _json_file = json.loads(line)
                author_id = _json_file.get("id")

                if author_id in UNIQUE_AUTHORS:
                    continue

                UNIQUE_AUTHORS.add(author_id)
                authors.append(DataExtractor.generate_author_row(_json_file))

                if len(authors) > 10_000:
                    CLIENT.copy_authors(authors)
                    authors = []

        CLIENT.copy_authors(authors)

    _authors_import()


#
# Tweets
#
def tweets_import():
    @timer_function("Tweets")
    def _tweets_import():
        with open(os.path.join(DATA_PATH, TWEETS_FILE), encoding="utf-8") as file:
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
                    CLIENT.copy_authors(authors)
                    CLIENT.copy_tweets(tweets)
                    tweets = []
                    authors = []

        CLIENT.copy_authors(authors)
        CLIENT.copy_tweets(tweets)
        UNIQUE_AUTHORS.clear()

    _tweets_import()


#
# Hashtags
#
def hashtags_import():
    @timer_function("Hashtags")
    def _hashtags_import():
        tag_id = 0

        with open(os.path.join(DATA_PATH, TWEETS_FILE), encoding="utf-8") as file:
            hashtags = []
            tweet_hashtags = []
            for line in file:
                _json_file = json.loads(line)
                tweet_id = _json_file.get("id", r"\N")

                for hashtag in DataExtractor.get_hashtags(_json_file):
                    if hashtag["tag"] not in UNIQUE_HASHTAGS:
                        UNIQUE_HASHTAGS[hashtag["tag"]] = tag_id
                        hashtag["id"] = tag_id
                        hashtags.append(hashtag)
                        tag_id += 1

                    tweet_hashtags.append({"tweet_id": tweet_id, "hashtag_id": UNIQUE_HASHTAGS[hashtag["tag"]]})

                if len(tweet_hashtags) > 10_000:
                    CLIENT.execute_hashtags(hashtags)
                    CLIENT.copy_tweet_hashtags(tweet_hashtags)
                    hashtags = []
                    tweet_hashtags = []

        CLIENT.execute_hashtags(hashtags)
        CLIENT.copy_tweet_hashtags(tweet_hashtags)
        UNIQUE_HASHTAGS.clear()

    _hashtags_import()


#
# Context entities filter
#
def context_entities_filter(context_entities):
    block_entries = []

    for context_entity in context_entities:
        context_entity_id = context_entity.get("id")

        if context_entity_id not in UNIQUE_ENTITIES:
            block_entries.append(context_entity)
            UNIQUE_ENTITIES.add(context_entity_id)

    return block_entries


#
# Context domains filter
#
def context_domains_filter(context_domains):
    block_entries = []

    for context_domain in context_domains:
        context_domain_id = context_domain.get("id")

        if context_domain_id not in UNIQUE_DOMAINS:
            block_entries.append(context_domain)
            UNIQUE_DOMAINS.add(context_domain_id)

    return block_entries


#
# Context items
#
def context_items_import():
    @timer_function("Context Items")
    def _context_items_import():
        with open(os.path.join(DATA_PATH, TWEETS_FILE), encoding="utf-8") as file:
            context_entities = []
            context_domains = []

            for line in file:
                _json_file = json.loads(line)

                context_entities.extend(context_entities_filter(DataExtractor.get_context_entities(_json_file)))
                context_domains.extend(context_domains_filter(DataExtractor.get_context_domains(_json_file)))

                if len(context_entities) > 10_000:
                    CLIENT.copy_context_entities(context_entities)
                    CLIENT.copy_context_domains(context_domains)
                    context_entities = []
                    context_domains = []

        CLIENT.copy_context_entities(context_entities)
        CLIENT.copy_context_domains(context_domains)
        UNIQUE_DOMAINS.clear()
        UNIQUE_ENTITIES.clear()

    _context_items_import()


#
# Tweet references
#
def tweet_references_import(unique_tweets: set):
    @timer_function("Tweet References")
    def _tweet_references_import():
        with open(os.path.join(DATA_PATH, TWEETS_FILE), encoding="utf-8") as file:
            block_entries = []

            for line in file:
                for tweet_reference in DataExtractor.generate_tweet_references(json.loads(line)):
                    parent_id = tweet_reference.get("parent_id")
                    if parent_id in unique_tweets:
                        block_entries.append(tweet_reference)

                if len(block_entries) > 100_000:
                    CLIENT.copy_tweet_references(block_entries)
                    block_entries = []

        CLIENT.copy_tweet_references(block_entries)

    _tweet_references_import()


#
# Context Annotations
#
def context_annotations_import():
    @timer_function("Context Annotations")
    def _context_annotations_import():
        with open(os.path.join(DATA_PATH, TWEETS_FILE), encoding="utf-8") as file:
            context_annotations = []

            for line in file:
                _json_file = json.loads(line)
                context_annotations.extend(DataExtractor.get_context_annotations_row(_json_file))
                if len(context_annotations) > 100_000:
                    CLIENT.copy_context_annotations(context_annotations)
                    context_annotations = []

            CLIENT.copy_context_annotations(context_annotations)

    _context_annotations_import()


#
# Links, Annotations
#
def N_rows_parse(lines):
    links = []
    annotations = []

    for line in lines:
        _json_file = json.loads(line)
        links.extend(DataExtractor.get_links_row(_json_file))
        annotations.extend(DataExtractor.get_annotations_row(_json_file))

        if len(links) > 10_000:
            CLIENT.copy_links(filter(lambda x: x is not None, links))
            links = []

        if len(annotations) > 10_000:
            CLIENT.copy_annotations(annotations)
            annotations = []

    CLIENT.copy_links(filter(lambda x: x is not None, links))
    CLIENT.copy_annotations(annotations)


def N_rows_import():
    @timer_function("Links, Annotations")
    def _N_rows_import():
        with open(os.path.join(DATA_PATH, TWEETS_FILE), encoding="utf-8") as file:
            lines = []
            for index, line in enumerate(file):
                lines.append(line)
                if index % 100_000 == 0:
                    N_rows_parse(lines)
                    lines = []

        N_rows_parse(lines)

    _N_rows_import()


@timer_function("Import")
def parallel_import():
    p = mp.Process(target=context_items_import, kwargs={})
    p.start()
    PROCS.append(p)

    authors_import()

    tweets_import()

    p = mp.Process(target=context_annotations_import, kwargs={})
    p.start()
    PROCS.append(p)

    p = mp.Process(target=hashtags_import, kwargs={})
    p.start()
    PROCS.append(p)

    p = mp.Process(target=tweet_references_import, kwargs={"unique_tweets": UNIQUE_TWEETS})
    p.start()
    PROCS.append(p)

    UNIQUE_TWEETS.clear()

    p = mp.Process(target=N_rows_import, kwargs={})
    p.start()
    PROCS.append(p)

    for p in PROCS:
        p.join()


if __name__ == "__main__":
    parallel_import()
