import os
import time

from langchain_community.document_loaders import ConfluenceLoader
import json
import psycopg2
from langchain_google_genai._common import GoogleGenerativeAIError
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

vector_store = PGVector(
    connection="postgresql+psycopg://user:postgres@db:5432/user",
    collection_name="embedding",
    embeddings=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07"),
    use_jsonb=True
)
text_splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,
    separator="\n"
)

connection = psycopg2.connect("host=db port=5432 dbname=user user=user")
cur = connection.cursor()
cur.execute("DROP TABLE IF EXISTS documents")
cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        document text NOT NULL
    )
""")
connection.commit()

loader = ConfluenceLoader(
    url=os.getenv("CONFLUENCE_URL"),
    username=os.getenv("CONFLUENCE_MAIL_ADDRESS"),
    api_key=os.getenv("CONFLUENCE_API_KEY"),
    space_key=os.getenv("CONFLUENCE_SPACE_KEY"),
    limit=10000
)


def with_retry(process, count=3):
    if count <= 0:
        return process()

    try:
        return process()
    except GoogleGenerativeAIError as e:
        print(f"Retry {count}", e)
        time.sleep(60)
        return with_retry(process, count-1)


def insert_all_documents():
    documents = loader.load()
    records = []
    for doc in documents:
        records.append(
            {
                'metadata': {**doc.metadata},
                'page_content': str(doc.page_content)
            }
        )

    # ドキュメント本文の投入
    for record in records:
        cur.execute("INSERT INTO documents(id, document) VALUES (%s, %s)", (record["metadata"]["id"], json.dumps(record)))
    connection.commit()
    # Embeddingしたデータの投入
    split_docs = text_splitter.split_documents(documents)
    with_retry(lambda: vector_store.add_documents(split_docs))


if __name__ == '__main__':
    insert_all_documents()
    connection.close()
