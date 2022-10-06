class DataExtractor:
    @staticmethod
    def generate_author_row(_input: dict = {}):
        public_metrics = _input.get("public_metrics", {})
        return {
            "id": _input.get("id", r"\N"),
            "name": _input.get("name", r"\N"),
            "username": _input.get("username", r"\N"),
            "description": _input.get("description", r"\N"),
            "followers_count": public_metrics.get("followers_count", 0),
            "following_count": public_metrics.get("following_count", 0),
            "tweet_count": public_metrics.get("tweet_count", 0),
            "listed_count": public_metrics.get("listed_count", 0),
        }

    @staticmethod
    def generate_tweet_row(_input: dict = {}):
        public_metrics = _input.get("public_metrics", {})
        return {
            "tweet": {
                "id": _input.get("id", r"\N"),
                "author_id": _input.get("author_id", r"\N"),
                "content": _input.get("text", r"\N"),
                "possibly_sensitive": _input.get("possibly_sensitive", r"\N"),
                "language": _input.get("lang", r"\N"),
                "source": _input.get("source", r"\N"),
                "retweet_count": public_metrics.get("retweet_count", 0),
                "reply_count": public_metrics.get("reply_count", 0),
                "like_count": public_metrics.get("like_count", 0),
                "quote_count": public_metrics.get("quote_count", 0),
                "created_at": _input.get("created_at", r"\N"),
            },
            "tweet_reference": DataExtractor.generate_tweet_reference_row(_input),
        }

    @staticmethod
    def generate_tweet_reference_row(_input: dict = {}):
        referenced_tweets = _input.get("referenced_tweets", {})
        return {
            "tweet_id": _input.get("id", r"\N"),
            "parent_id": referenced_tweets.get("id", r"\N"),
            "type": referenced_tweets.get("type", r"\N"),
        }

    @staticmethod
    def get_hashtags(_entity: dict = {}):
        return _entity.get("hashtags", {}).get("tag", r"\N")

    @staticmethod
    def generate_tweet_hashtags_row(_input: dict = {}):
        referenced_tweets = _input.get("referenced_tweets", {})
        return {
            "tweet_id": _input.get("id", r"\N"),
            "parent_id": referenced_tweets.get("id", r"\N"),
            "type": referenced_tweets.get("type", r"\N"),
        }

    @staticmethod
    def get_entities(_input: dict = {}):
        return _input.get("entities", {})

    @staticmethod
    def get_links_row(tweet_id: str, _entity: dict = {}):
        urls = _entity.get("urls", {})
        url = urls.get("expanded_url", r"\N")
        if len(url) > 2048:
            return
        return {
            "tweet_id": tweet_id,
            "url": url,
            "title": urls.get("title", r"\N"),
            "description": urls.get("description", r"\N"),
        }

    @staticmethod
    def get_annotations_row(tweet_id: str, _entity: dict = {}):
        annotations = _entity.get("annotations", {})
        return {
            "tweet_id": tweet_id,
            "value": annotations.get("normalized_text", r"\N"),
            "type": annotations.get("type", r"\N"),
            "probability": annotations.get("probability", r"\N"),
        }

    @staticmethod
    def get_context_annotations_row(tweet_id: str, _input: dict = {}):
        context_annotations = _input.get("context_annotations", {})
        return {
            "context_annotations": {
                "tweet_id": tweet_id,
                "context_domain_id": context_annotations.get("domain", r"\N"),
                "context_entity_id": context_annotations.get("entity", r"\N"),
            },
            "context_entities": DataExtractor.get_context_entities_row(
                context_annotations
            ),
            "context_domains": DataExtractor.get_context_domains_row(
                context_annotations
            ),
        }

    @staticmethod
    def get_context_entities_row(context_annotations: dict = {}):
        context_entities = context_annotations.get("entities", {})
        return {
            "id": context_entities.get("id", r"\N"),
            "name": context_entities.get("name", r"\N"),
            "description": context_entities.get("description", r"\N"),
        }

    @staticmethod
    def get_context_domains_row(context_annotations: dict = {}):
        context_domains = context_annotations.get("context_domains", {})
        return {
            "id": context_domains.get("id", r"\N"),
            "name": context_domains.get("name", r"\N"),
            "description": context_domains.get("description", r"\N"),
        }
