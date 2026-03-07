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
        
        # Полный промпт с CoT и few-shot
        prompt = SYSTEM_PROMPT.format(
            examples=examples_text,
            question=question,
            context=context
        )
        
        return prompt
    
    def answer(self, question, k=4):
        """
        Основной метод: принимает вопрос, возвращает ответ
        """
        print(f"\n--- Обработка вопроса: {question} ---")
        
        # 1. Поиск релевантных чанков
        print("Поиск в векторной базе...")
        context_chunks = self.vectordb.similarity_search(question, k=k)
        
        # Проверяем, есть ли найденные чанки
        if not context_chunks:
            return "Я не знаю. В базе знаний нет информации по вашему вопросу."
        
        print(f"Найдено чанков: {len(context_chunks)}")
        
        # 2. Формирование промпта
        prompt = self._build_prompt(question, context_chunks)
        
        # 3. Генерация ответа
        print("Генерация ответа LLM...")
        answer = self.llm.invoke(prompt)
        
        return answer
    
    def answer_with_sources(self, question, k=4):
        """
        Возвращает ответ вместе с источниками (для отладки)
        """
        context_chunks = self.vectordb.similarity_search(question, k=k)
        
        if not context_chunks:
            return "Я не знаю.", []
        
        prompt = self._build_prompt(question, context_chunks)
        answer = self.llm.invoke(prompt)
        
        # Собираем источники
        sources = []
        for chunk in context_chunks:
            source = chunk.metadata.get('source', 'Неизвестный источник')
            text_preview = chunk.page_content[:100] + "..."
            sources.append(f"{source}: {text_preview}")
        
        return answer, sources