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
            for author in tweets:
                csv_file_like_object.write(
                    "\t".join(
                        map(
                            str,
                            (
                                author["id"],
                                author["author_id"],
                                clean_csv_value(author["content"]),
                                author["possibly_sensitive"],
                                author["language"],
                                clean_csv_value(author["source"]),
                                author["retweet_count"],
                                author["reply_count"],
                                author["like_count"],
                                author["quote_count"],
                                author["created_at"],
                            ),
                        )
                    )
                    + "\n"
                )
            csv_file_like_object.seek(0)
            cursor.copy_from(csv_file_like_object, "tweets", sep="\t")
