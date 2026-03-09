import os
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

vectordb = Chroma(persist_directory="./chroma_db", embedding_function=embedding_model)

test_queries = [
    "When the Stankin was founded?",
    "What is a Suicide Squad?",
    "Name of snow-white pigeon?",
    "Кто основатель Suicide Squad?"
]

for query in test_queries:
    print(f"\n--- Запрос: {query} ---")

    results = vectordb.similarity_search(query, k=3)

    for i, doc in enumerate(results):
        print(f"\nРезультат {i+1}:")
        print(f"Источник: {doc.metadata.get('source', 'неизвестно')}")
        print(f"Текст: {doc.page_content[:200]}...")  # первые 200 символов
        print("-" * 50)