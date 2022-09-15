import argparse
from abc import ABC, abstractclassmethod, abstractmethod
from uuid import uuid4

import psycopg2
from flask import Flask, request

DB = psycopg2.connect('postgresql://postgres:postgres@db/postgres')

app = Flask('url_shortening')


class Storage(ABC):
    @abstractmethod
    def get(url_id):
        pass

    @abstractmethod
    def save(url):
        pass


class MemoryStorage(Storage):
    def __init__(self):
        self.storage = {}

    def get(self, url_id):
        return self.storage.get(url_id)

    def save(self, url):
        url_id = str(uuid4())
        self.storage[url_id] = url
        return url_id


class PostgresStorage(Storage):
    def __init__(self, conn):
        self.conn = conn

    def get(self, url_id):
        with self.conn.cursor() as cur:
            sql = """
                SELECT url FROM urls WHERE id = %s::uuid;
            """
            cur.execute(sql, (url_id, ))
            url = cur.fetchone()[0]
        return url

    def save(self, url):
        with self.conn.cursor() as cur:
            sql = """
                INSERT INTO urls (id, url)
                VALUES (gen_random_uuid(), %s)
                RETURNING id
            """
            cur.execute(sql, (url, ))
            url_id = cur.fetchone()[0]
        return url_id


parser = argparse.ArgumentParser(description='Shortens url')
parser.add_argument('-d', '--db', action='store_true',
                    help='Activates storing in DB')
ARGS = parser.parse_args()
# args is False by default
# when starting with -d flag it becomes True.

if ARGS.db == True:
    store = PostgresStorage(DB)
    print('Running in postgres mode')
else:
    store = MemoryStorage()
    print('Running in memory mode')


@app.route('/', methods=['POST'])
def short_url():
    # saves original url and returns the shortened version
    json_args = request.json
    url = json_args['url']
    url_to_return = store.save(url)
    return {
        'url': f'{request.base_url}/{url_to_return}'
    }


@app.route('/<url_id>', methods=['GET'])
def expand(url_id):
    # returns original url upon visiting
    url_to_return = store.get(url_id)
    return {
        'url': url_to_return,
    }


def init_db():
    # creates DB for storing links and their shortening version
    cur = DB.cursor()

    sql = """
    CREATE TABLE IF NOT EXISTS urls (
        id UUID NOT NULL PRIMARY KEY,
        url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT current_timestamp
    )
    """

    cur.execute(sql)
    DB.commit()
    cur.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=False)
