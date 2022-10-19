from Tools import clean_csv_value


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
        }

    @staticmethod
    def generate_tweet_references(_input: dict = {}):
        referenced_tweets = _input.get("referenced_tweets", {})
        for referenced_tweet in referenced_tweets:
            yield {
                "tweet_id": _input.get("id", r"\N"),
                "parent_id": referenced_tweet.get("id", r"\N"),
                "type": referenced_tweet.get("type", r"\N"),
            }

    @staticmethod
    def get_hashtags(_input: dict = {}):
        for hashtag in _input.get("entities", {}).get("hashtags", {}):
            yield {"tag": hashtag.get("tag", r"\N")}

    @staticmethod
    def get_entities(_input: dict = {}):
        return _input.get("entities", {})

    @staticmethod
    def get_links_row(_input: dict = {}):
        urls = _input.get("entities", {}).get("urls", {})
        for url_entity in urls:
            _url = url_entity.get("expanded_url", r"\N")
            if len(clean_csv_value(_url)) > 2048:
                yield
            else:
                yield {
                    "tweet_id": _input.get("id", r"\N"),
                    "url": _url,
                    "title": url_entity.get("title", r"\N"),
                    "description": url_entity.get("description", r"\N"),
                }

    @staticmethod
    def get_annotations_row(_input: dict = {}):
        annotations = _input.get("entities", {}).get("annotations", {})
        for annotation in annotations:
            yield {
                "tweet_id": _input.get("id", r"\N"),
                "value": annotation.get("normalized_text", r"\N"),
                "type": annotation.get("type", r"\N"),
                "probability": annotation.get("probability", r"\N"),
            }

    @staticmethod
    def get_context_annotations_row(_input: dict = {}):
        tweet_id = _input.get("id", r"\N")
        context_items = _input.get("context_annotations", {})

        for context_item in context_items:
            yield {
                "tweet_id": tweet_id,
                "context_domain_id": context_item.get("domain", {}).get("id", r"\N"),
                "context_entity_id": context_item.get("entity", {}).get("id", r"\N"),
            }

    @staticmethod
    def get_context_entities(_input: dict = {}):
        context_items = _input.get("context_annotations", {})
        for context_item in context_items:
            context_entity = context_item.get("entity", {})
            yield {
                "id": context_entity.get("id", r"\N"),
                "name": context_entity.get("name", r"\N"),
                "description": context_entity.get("description", r"\N"),
            }

    @staticmethod
    def get_context_domains(_input: dict = {}):
        context_items = _input.get("context_annotations", {})
        for context_item in context_items:
            context_domain = context_item.get("domain", {})
            yield {
                "id": context_domain.get("id", r"\N"),
                "name": context_domain.get("name", r"\N"),
                "description": context_domain.get("description", r"\N"),
            }
