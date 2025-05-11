import time

import psycopg2
from langchain_google_genai._common import GoogleGenerativeAIError
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

connection = psycopg2.connect("host=db port=5432 dbname=user user=user")
cur = connection.cursor()

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


def with_retry(process, count=3):
    if count <= 0:
        return process()

    try:
        return process()
    except GoogleGenerativeAIError as e:
        print(f"Retry {count}", e)
        time.sleep(10)
        return with_retry(process, count-1)


def search_all(query_list: list[str]):
    return [with_retry(lambda:search(query)) for query in query_list]


def search(query: str):
    documents = vector_store.similarity_search(query=query, k=5)
    search_results = []
    for doc in documents:
        search_results.append(
            {
                "title": doc.metadata["title"],
                "url": doc.metadata["source"],
                "raw_content": str(doc.page_content)
            }
        )
    return {
        "query": query,
        "results": search_results
    }
