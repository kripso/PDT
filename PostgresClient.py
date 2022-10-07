from distutils.command.clean import clean
from typing import Iterator, Dict, Any
import io
from Tools import clean_csv_value
import psycopg2.extras


class PostgresClient:
    @staticmethod
    def copy_authors(connection, authors: Iterator[Dict[str, Any]]) -> None:
        with connection.cursor() as cursor:
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
    def copy_tweets(connection, tweets: Iterator[Dict[str, Any]]) -> None:
        with connection.cursor() as cursor:
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
    def copy_context_entities(
        connection, context_entities: Iterator[Dict[str, Any]]
    ) -> None:
        with connection.cursor() as cursor:
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
    def copy_context_domains(
        connection, context_domains: Iterator[Dict[str, Any]]
    ) -> None:
        with connection.cursor() as cursor:
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
    def copy_context_annotations(
        connection, context_annotations: Iterator[Dict[str, Any]]
    ) -> None:
        with connection.cursor() as cursor:
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
    def copy_tweet_references(
        connection, tweet_references: Iterator[Dict[str, Any]]
    ) -> None:
        with connection.cursor() as cursor:
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
    def copy_annotations(connection, annotations: Iterator[Dict[str, Any]]) -> None:
        with connection.cursor() as cursor:
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
    def copy_links(connection, links: Iterator[Dict[str, Any]]) -> None:
        with connection.cursor() as cursor:
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

    # @staticmethod
    # def copy_hashtags(connection, hashtags: Iterator) -> None:
    #     with connection.cursor() as cursor:
    #         csv_file_like_object = io.StringIO()
    #         for hashtag in hashtags:
    #             csv_file_like_object.write(f"{clean_csv_value(hashtag)}\n")
    #         csv_file_like_object.seek(0)
    #         cursor.copy_from(
    #             csv_file_like_object,
    #             "hashtags",
    #             sep="\t",
    #             columns=["tag"],
    #         )

    def execute_hashtags(
        connection,
        hashtags: Iterator,
        page_size: int = 100,
    ) -> None:
        with connection.cursor() as cursor:
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
                page_size=page_size,
            )

    @staticmethod
    def copy_tweet_hashtags(
        connection, tweet_hashtags: Iterator[Dict[str, Any]]
    ) -> None:
        with connection.cursor() as cursor:
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
