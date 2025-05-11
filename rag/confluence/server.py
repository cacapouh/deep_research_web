import json
from bottle import route, run
import psycopg2


connection = psycopg2.connect("host=db port=5432 dbname=user user=user")
cur = connection.cursor()


@route('/documents')
def route_documents():
    result = []
    cur.execute("SELECT * FROM documents")
    for record in cur:
        result.append(json.loads(record[1]))
    return json.dumps(result)


@route('/documents/<doc_id>')
def route_documents_id(doc_id):
    cur.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))
    record = cur.fetchone()
    if record:
        return record[1]
    return None


@route('/ready')
def route_ready():
    return "OK"


if __name__ == '__main__':
    run(host='0.0.0.0', port=18080)
    connection.close()
