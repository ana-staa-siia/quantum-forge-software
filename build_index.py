import os
import time
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

print("Загрузка документов...")
DOCS_DIR = "knowledge_base/"

documents = []
for filename in os.listdir(DOCS_DIR):
    if filename.endswith(".txt"):
        loader = TextLoader(os.path.join(DOCS_DIR, filename))
        documents.extend(loader.load())

print(f"Загружено файлов: {len(documents)}")
# =====================================
print("Разбиение на чанки...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " ", ""]
)
chunks = text_splitter.split_documents(documents)
print(f"Получено чанков: {len(chunks)}")
# =====================================
print("Создание эмбеддингов и индекса...")
start_time = time.time()

embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

vectordb = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="./chroma_db"
)

vectordb.persist()
# =====================================
end_time = time.time()
print(f"Индексация заняла {end_time - start_time:.2f} секунд")

print("\nГотово! Индекс сохранён в папке ./chroma_db")