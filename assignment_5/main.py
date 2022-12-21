from datetime import datetime

import psycopg2
from elasticsearch import Elasticsearch
from elasticsearch import helpers

if __name__ == '__main__':
    es = Elasticsearch()

    try:
        conn = psycopg2.connect(host='localhost',
                                user='postgres',
                                password='postgres',
                                dbname='tweets_db')
    except:
        print("Unable to connect to the database")

    with conn.cursor(name='cur') as cursor:
        query = 'SELECT * FROM tweets_all;'
        cursor.execute(query)
        i = 0
        lst = []
        for row in cursor:
            i = i + 1
            row_json = {}
            row_json['_index'] = 'tweets_idx'
            row_json['_id'] = str(row[0])
            row_json['content'] = row[1]
            row_json['retweet_count'] = row[3]
            row_json['favorite_count'] = row[4]
            row_json['happened_at'] = datetime.strftime(row[5].replace(tzinfo=None), '%Y-%m-%d %H:%M:%S')

            # author
            row_json['author'] = {'id': str(row[6]), 'screen_name': row[7], 'name': row[8]}
            if row[9] and row[9] != "":
                row_json['author']['description'] = str(row[9])
            if row[10]:
                row_json['author']['followers_count'] = row[10]
            if row[11]:
                row_json['author']['friends_count'] = row[11]
            if row[12]:
                row_json['author']['statuses_count'] = row[12]

            # country
            if row[13]:
                row_json['country'] = {'id': str(row[13]), 'code': row[14], 'name': row[15]}

            # parent
            if row[16]:
                row_json['tweet_parent'] = {'id': str(row[16]), 'content': row[17]}

            if row[29]:
                row_json['neg'] = row[29]
            if row[30]:
                row_json['neu'] = row[30]
            if row[31]:
                row_json['pos'] = row[31]
            if row[32]:
                row_json['compound'] = row[32]

            # hashtags
            if row[33][0] is not None:
                row_json['hashtags'] = []
                for hashtag in row[33]:
                    row_json['hashtags'].append(hashtag)

            # mentions
            if row[34][0] is not None:
                row_json['mentions'] = []
                for mention in row[34]:
                    row_json['mentions'].append({'name': mention})

            # theories
            if row[35][0] is not None:
                row_json['theories'] = []
                for theory in row[35]:
                    row_json['theories'].append(theory)

            lst.append(row_json)
            if i % 10000 == 0:
                print(i)
                helpers.bulk(es, lst)
                lst = []

        if len(lst) > 0:
            helpers.bulk(es, lst)
