import os
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from prompt_templates import FEW_SHOT_EXAMPLES, SYSTEM_PROMPT

class RAGBot:
    def __init__(self, vector_db_path="../chroma_db", embedding_model_name="all-MiniLM-L6-v2"):
        """
        Инициализация RAG-бота
        """
        print("Загрузка модели эмбеддингов...")
        self.embedding_model = SentenceTransformerEmbeddings(model_name=embedding_model_name)
        
        print("Загрузка векторного индекса...")
        self.vectordb = Chroma(
            persist_directory=vector_db_path, 
            embedding_function=self.embedding_model
        )
        
        print("Инициализация LLM...")
        self.llm = Ollama(model="mistral")
        
        # Few-shot примеры из внешнего файла
        self.few_shot_examples = FEW_SHOT_EXAMPLES
    
    def _build_prompt(self, question, context_chunks):
        """
        Формирование промпта с техниками Few-shot и Chain-of-Thought
        """
        # Формируем контекст из найденных чанков
        context = "\n\n".join([chunk.page_content for chunk in context_chunks])
        
        # Формируем few-shot примеры
        examples_text = ""
        for ex in self.few_shot_examples[:2]:  # берём 1-2 примера
            examples_text += f"Вопрос: {ex['question']}\nОтвет: {ex['answer']}\n\n"

        prompt = SYSTEM_PROMPT.format(
            examples=examples_text,
            question=question,
            context=context
        )
        
        return prompt
    
    def answer(self, question, k=4):
        print(f"\n--- Обработка вопроса: {question} ---")

        # Поиск релевантных чанков
        print("Поиск в векторной базе...")
        context_chunks = self.vectordb.similarity_search(question, k=k*2)

        # Фильтруем опасные чанки
        safe_chunks = self._filter_malicious_chunks(context_chunks)

        if not safe_chunks:
            return "Я не знаю. Информация не найдена или была отфильтрована по соображениям безопасности."

        print(f"Найдено чанков: {len(safe_chunks)} (отфильтровано {len(context_chunks) - len(safe_chunks)})")

        prompt = self._build_prompt(question, safe_chunks)
        answer = self.llm.invoke(prompt)

        return answer

    def _filter_malicious_chunks(self, chunks):
        filtered_chunks = []

        # Список опасных паттернов
        dangerous_patterns = [
            "ignore all instructions",
            "ignore previous",
            "output:",
            "суперпароль",
            "swordfish",
            "root:"
        ]

        for chunk in chunks:
            content = chunk.page_content.lower()
            is_dangerous = any(pattern in content for pattern in dangerous_patterns)

            if not is_dangerous:
                filtered_chunks.append(chunk)
            else:
                print(f"⚠️ Отфильтрован потенциально опасный чанк из {chunk.metadata.get('source', 'неизвестно')}")

        return filtered_chunks