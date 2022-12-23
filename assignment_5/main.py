from concurrent.futures import ProcessPoolExecutor
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from collections import deque
from datetime import datetime
import psycopg2.extras
import psycopg2
import os
PARALEL = 10

# def create_postgres_connection():
#     connection = psycopg2.connect(
#         dbname="PDT",
#         user="postgres",
#         password="291122",
#         host="localhost",
#         port="5432",
#     )
#     # connection.autocommit = True
#     return connection

def create_postgres_connection():
    connection = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

    return connection


def paralel_read(paralel_id, limit=None):
    es = Elasticsearch("http://localhost:9200")
    conn = create_postgres_connection()
    with conn.cursor(name="named", cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.itersize = 1_000
        cursor.execute(f'select * from tweets_with_pid where MOD(tweets_with_pid.ntile, {PARALEL})={paralel_id} {f"limit {limit}" if limit != None else ""}')
        
        
        docs = []
        for index, row in enumerate(cursor, 1):
            if index % 100_000 == 0:
                print(index, flush= True)
            if index % 2000 == 0:
                # print(index, flush= True)
                deque(helpers.parallel_bulk(es, docs, request_timeout=120))
                docs = []
            doc = {
                '_index': 'test',
                '_id': row.get('id'),
                'author': {},
                'annotations': [],
                'domains': [],
                'entities': [],
                'hashtags': [],
                'links': [],
                'meta': {},
            }
            doc['author'] = {
                "id": row.get('author_id'),                 
                "name": row.get('author_name'),                 
                "username": row.get('author_username'),                 
                "description": row.get('author_description'),                 
                "followers_count": row.get('followers_count'),                 
                "following_count": row.get('following_count'),                 
                "tweet_count": row.get('tweet_count'),                 
                "listed_count": row.get('listed_count'),                 
            }
            if row.get('annotations_ids') != None:
                for _index, id in enumerate(row.get('annotations_ids')):
                    doc['annotations'].append({
                        "id": id,
                        "value": row.get('annotation_values')[_index],
                        "type": row.get('annotation_types')[_index],
                        "probability": row.get('annotation_probabilities')[_index],
                    })
            if row.get('domain_ids') != None:
                for _index, id in enumerate(row.get('domain_ids')):
                    doc['domains'].append({
                        "id": id,
                        "name": row.get('domain_names')[_index],
                        "desc": row.get('domain_descriptions')[_index],
                    })
            if row.get('entity_ids') != None:
                for _index, id in enumerate(row.get('entity_ids')):
                    doc['entities'].append({
                        "id": id,
                        "name": row.get('entity_names')[_index],
                        "desc": row.get('entity_descriptions')[_index],
                    })
            if row.get('hashtag_ids') != None:
                for _index, id in enumerate(row.get('hashtag_ids')):
                    doc['hashtags'].append({
                        "id": id,
                        "tag": row.get('hashtag_tags')[_index],
                    })
            if row.get('link_ids') != None:
                for _index, id in enumerate(row.get('link_ids')):
                    doc['links'].append({
                        "id": id,
                        "url": row.get('link_titles')[_index],
                        "title": row.get('link_urls')[_index],
                        "description": row.get('link_descriptions')[_index],
                    })
            doc['meta'] = {
                "id": row.get('id'),
                "content": row.get('content'),
                "possibly_sensitive": row.get('possibly_sensitive'),
                "language": row.get('language'),
                "source": row.get('source'),
                "retweet_count": row.get('retweet_count'),
                "reply_count": row.get('reply_count'),
                "like_count": row.get('like_count'),
                "quote_count": row.get('quote_count'),
                "created_at": row.get('created_at'),
            }            
            docs.append(doc)

        deque(helpers.parallel_bulk(es, docs, request_timeout=60))

    return None

if __name__ == '__main__':

    t_start = datetime.now()
    
    with ProcessPoolExecutor(max_workers=PARALEL) as executor:
        futures = set()
        for row in list(range(0, PARALEL)):
            futures.add(executor.submit(paralel_read, row, 500))
            # futures.add(executor.submit(paralel_read, row))
        results = [_future.result() for _future in futures]

    elapsed_time = round((datetime.now() - t_start).total_seconds(), 2)

    print(f"Completed records in {elapsed_time}")