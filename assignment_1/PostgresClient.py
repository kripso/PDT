from Tools import clean_csv_value, create_postgres_connection
from typing import Iterator, Dict, Any
import psycopg2.extras
import threading
import io


class PostgresClient:
    def __init__(self) -> None:
        self.threads = []
        self.connection = create_postgres_connection()

    def on_call(func):
        def inner(self, _func, _kwargs, last=False):
            if len(self.threads) == 10:
                for t in self.threads:
                    t.join()

                self.threads = []

            func(self, _func, _kwargs, last)

        return inner

    @on_call
    def threaded(self, _func, kwargs, last=False):
        t = threading.Thread(target=_func, kwargs=(kwargs))
        t.start()
        self.threads.append(t)

        if last:
            for t in self.threads:
                t.join()

            self.threads = []

    @staticmethod
    def copy_authors(authors: Iterator[Dict[str, Any]]) -> None:
        with create_postgres_connection().cursor() as cursor:
            csv_file_like_object = io.StringIO()
            for author in authors:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            str,
                            (
                                author["id"],
                                clean_csv_value(author["name"]),
                                clean_csv_value(author["username"]),
                                clean_csv_value(author["description"]),
                                author["followers_count"],
                                author["following_count"],
                                author["tweet_count"],
                                author["listed_count"],
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(csv_file_like_object, "authors", sep="\t")

    @staticmethod
    def copy_tweets(tweets: Iterator[Dict[str, Any]]) -> None:
        with create_postgres_connection().cursor() as cursor:
            csv_file_like_object = io.StringIO()
            for tweet in tweets:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            str,
                            (
                                tweet["id"],
                                tweet["author_id"],
                                clean_csv_value(tweet["content"]),
                                tweet["possibly_sensitive"],
                                tweet["language"],
                                clean_csv_value(tweet["source"]),
                                tweet["retweet_count"],
                                tweet["reply_count"],
                                tweet["like_count"],
                                tweet["quote_count"],
                                tweet["created_at"],
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(csv_file_like_object, "tweets", sep="\t")

    @staticmethod
    def copy_context_entities(context_entities: Iterator[Dict[str, Any]]) -> None:
        with create_postgres_connection().cursor() as cursor:
            csv_file_like_object = io.StringIO()
            for context_entity in context_entities:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            clean_csv_value,
                            (
                                context_entity["id"],
                                context_entity["name"],
                                context_entity["description"],
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(csv_file_like_object, "context_entities", sep="\t")

    @staticmethod
    def copy_context_domains(context_domains: Iterator[Dict[str, Any]]) -> None:
        with create_postgres_connection().cursor() as cursor:
            csv_file_like_object = io.StringIO()
            for context_domain in context_domains:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            clean_csv_value,
                            (
                                context_domain["id"],
                                context_domain["name"],
                                context_domain["description"],
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(csv_file_like_object, "context_domains", sep="\t")

    @staticmethod
    def copy_context_annotations(context_annotations: Iterator[Dict[str, Any]]) -> None:
        with create_postgres_connection().cursor() as cursor:
            csv_file_like_object = io.StringIO()
            for context_annotation in context_annotations:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            str,
                            (
                                context_annotation["tweet_id"],
                                context_annotation["context_domain_id"],
                                context_annotation["context_entity_id"],
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(
                csv_file_like_object,
                "context_annotations",
                sep="\t",
                columns=["tweet_id", "context_domain_id", "context_entity_id"],
            )

    @staticmethod
    def copy_tweet_references(tweet_references: Iterator[Dict[str, Any]]) -> None:
        with create_postgres_connection().cursor() as cursor:
            csv_file_like_object = io.StringIO()
            for tweet_reference in tweet_references:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            str,
                            (
                                tweet_reference["tweet_id"],
                                tweet_reference["parent_id"],
                                clean_csv_value(tweet_reference["type"]),
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(
                csv_file_like_object,
                "tweet_references",
                sep="\t",
                columns=["tweet_id", "parent_id", "type"],
            )

    @staticmethod
    def copy_annotations(annotations: Iterator[Dict[str, Any]]) -> None:
        with create_postgres_connection().cursor() as cursor:
            csv_file_like_object = io.StringIO()
            for annotation in annotations:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            str,
                            (
                                annotation["tweet_id"],
                                clean_csv_value(annotation["value"]),
                                clean_csv_value(annotation["type"]),
                                annotation["probability"],
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(
                csv_file_like_object,
                "annotations",
                sep="\t",
                columns=["tweet_id", "value", "type", "probability"],
            )

    @staticmethod
    def copy_links(links: Iterator[Dict[str, Any]]) -> None:
        with create_postgres_connection().cursor() as cursor:
            csv_file_like_object = io.StringIO()
            for link in links:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            clean_csv_value,
                            (
                                link["tweet_id"],
                                link["url"],
                                link["title"],
                                link["description"],
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(
                csv_file_like_object,
                "links",
                sep="\t",
                columns=["tweet_id", "url", "title", "description"],
            )

    @staticmethod
    def execute_hashtags(hashtags: Iterator) -> None:
        with create_postgres_connection().cursor() as cursor:
            psycopg2.extras.execute_values(
                cursor,
                """
                INSERT INTO hashtags(id, tag) VALUES %s ON CONFLICT DO NOTHING;
            """,
                (
                    (
                        hashtag["id"],
                        clean_csv_value(hashtag["tag"]),
                    )
                    for hashtag in hashtags
                ),
                page_size=1000,
            )

    @staticmethod
    def copy_tweet_hashtags(tweet_hashtags: Iterator[Dict[str, Any]]) -> None:
        with create_postgres_connection().cursor() as cursor:
            csv_file_like_object = io.StringIO()
            for tweet_hashtag in tweet_hashtags:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            str,
                            (
                                tweet_hashtag["tweet_id"],
                                tweet_hashtag["hashtag_id"],
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(
                csv_file_like_object,
                "tweet_hashtags",
                sep="\t",
                columns=["tweet_id", "hashtag_id"],
            )
