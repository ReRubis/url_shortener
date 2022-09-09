import argparse
import uuid

import psycopg2
from flask import Flask, request

DB = psycopg2.connect('postgresql://postgres:postgres@db/postgres')
app = Flask('url_shortening')

MEMORY_STORAGE = {}

parser = argparse.ArgumentParser(description='Shortens url')
parser.add_argument('-d', '--db', action='store_true',
                    help='Activates storing in DB')
ARGS = parser.parse_args()
# args is False by default
# when starting with -d flag it becomes True.


@app.route('/', methods=['POST'])
def short_url():
    # saves original url and returns the shortened version
    json_args = request.json
    url = json_args['url']
    if ARGS.db == True:
        cur = DB.cursor()

        sql = """
            INSERT INTO urls (id, url)
            VALUES (gen_random_uuid(), %s)
            RETURNING id
        """
        cur.execute(sql, (url, ))

        row = cur.fetchone()
        generated_uuid = row[0]
        DB.commit()
        cur.close()

    else:
        generated_uuid = str(uuid.uuid4())
        MEMORY_STORAGE[generated_uuid] = url

    return {
        'url': f'{request.base_url}/{generated_uuid}',
    }


@app.route('/<url_id>', methods=['GET'])
def expand(url_id):
    # returns original url upon visiting
    if ARGS.db == True:
        cur = DB.cursor()

        sql = """
            SELECT url FROM urls WHERE id = %s::uuid;
        """
        cur.execute(sql, (url_id,))

        row = cur.fetchone()
        cur.close()
        url = row[0]

    else:
        url = MEMORY_STORAGE[url_id]

    return {
        'url': url,
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
