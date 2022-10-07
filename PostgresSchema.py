class PostgresSchema:
    @staticmethod
    def create_authors_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS authors CASCADE;
            CREATE UNLOGGED TABLE authors (
                id                      BIGINT PRIMARY KEY,
                name                    VARCHAR ( 255 ),
                username                VARCHAR ( 255 ),
                description             TEXT,
                followers_count         INTEGER,
                following_count         INTEGER,
                tweet_count             INTEGER,
                listed_count            INTEGER
            );
        """
        )

    @staticmethod
    def create_context_domains_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS context_domains CASCADE;
            CREATE UNLOGGED TABLE context_domains (
                id                      BIGINT PRIMARY KEY,
                name                    VARCHAR ( 255 ) NOT NULL,
                description             TEXT
            );
        """
        )

    @staticmethod
    def create_context_entities_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS context_entities CASCADE;
            CREATE UNLOGGED TABLE context_entities (
                id                      BIGINT PRIMARY KEY,
                name                    VARCHAR ( 255 ) NOT NULL,
                description             TEXT
            );
        """
        )

    # GENERATED ALWAYS AS IDENTITY,
    @staticmethod
    def create_context_annotations_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS context_annotations CASCADE;
            CREATE UNLOGGED TABLE context_annotations (
                id                      BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                tweet_id                BIGINT REFERENCES tweets(id) NOT NULL,
                context_domain_id       BIGINT REFERENCES context_domains(id) NOT NULL,
                context_entity_id       BIGINT REFERENCES context_entities(id) NOT NULL
            );
        """
        )

    @staticmethod
    def create_annotations_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS annotations  CASCADE;
            CREATE UNLOGGED TABLE annotations (
                id                      BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                tweet_id                BIGINT REFERENCES tweets(id) NOT NULL,
                value                   TEXT NOT NULL,
                type                    TEXT NOT NULL,
                probability             NUMERIC(4,3) NOT NULL
            );
        """
        )

    @staticmethod
    def create_links_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS links CASCADE;
            CREATE UNLOGGED TABLE links (
                id                      BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                tweet_id                BIGINT REFERENCES tweets(id) NOT NULL,
                url                     VARCHAR ( 2048 ) NOT NULL,
                title                   TEXT,
                description             TEXT
            );
        """
        )

    @staticmethod
    def create_tweet_references_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS tweet_references CASCADE;
            CREATE UNLOGGED TABLE tweet_references (
                id                      BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                tweet_id                BIGINT REFERENCES tweets(id) NOT NULL,
                parent_id               BIGINT REFERENCES tweets(id) NOT NULL,
                type                    VARCHAR ( 20 ) NOT NULL
            );
        """
        )

    @staticmethod
    def create_hashtags_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS hashtags CASCADE;
            CREATE UNLOGGED TABLE hashtags (
                id                      BIGINT PRIMARY KEY,
                tag                     TEXT UNIQUE
            );
        """
        )

    @staticmethod
    def create_tweet_hashtags_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS tweet_hashtags CASCADE;
            CREATE UNLOGGED TABLE tweet_hashtags (
                id                      BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                tweet_id                BIGINT REFERENCES tweets(id) NOT NULL,
                hashtag_id              BIGINT REFERENCES hashtags(id) NOT NULL
            );
        """
        )

    @staticmethod
    def create_tweets_table(cursor) -> None:
        cursor.execute(
            """
            DROP TABLE IF EXISTS tweets CASCADE;
            CREATE UNLOGGED TABLE tweets (
                id                      BIGINT PRIMARY KEY,
                author_id               BIGINT REFERENCES authors(id) NOT NULL,
                content                 TEXT NOT NULL,
                possibly_sensitive      BOOL NOT NULL,
                language                VARCHAR ( 3 ) NOT NULL,
                source                  TEXT NOT NULL,
                retweet_count           INTEGER,
                reply_count             INTEGER,
                like_count              INTEGER,
                quote_count             INTEGER,
                created_at              TIMESTAMPTZ
            );
        """
        )
