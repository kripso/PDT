from distutils.command.clean import clean
from typing import Iterator, Dict, Any
import io
from Tools import clean_csv_value


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
