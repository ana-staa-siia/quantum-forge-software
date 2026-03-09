from init_bot import RAGBot
import sys

def print_help():
    print("""
Команды:
  /help    - показать эту справку
  /sources - включить/выключить показ источников
  /exit    - выйти
  /clear   - очистить экран
  Любой текст - задать вопрос боту
    """)

def clear_screen():
    """Очистка экрана"""
    import os
    os.system('clear' if os.name == 'posix' else 'cls')

def main():
    print("=" * 60)
    print("   RAG-бот QuantumForge (консольная версия)")
    print("=" * 60)

    # Инициализация бота
    try:
        bot = RAGBot()
    except Exception as e:
        print(f"Ошибка при инициализации бота: {e}")
        print("Убедитесь, что:")
        print("1. Установлен Ollama (brew install ollama)")
        print("2. Загружена модель (ollama pull mistral)")
        print("3. Индекс создан (папка ./chroma_db существует)")
        sys.exit(1)

    print_help()

    while True:
        try:
            # Получаем ввод пользователя
            user_input = input("\n👤 Ваш вопрос: ").strip()

            if not user_input:
                continue

            # Обработка команд
            if user_input.lower() == '/exit':
                print("До свидания!")
                break
            elif user_input.lower() == '/help':
                print_help()
                continue
            elif user_input.lower() == '/clear':
                clear_screen()
                continue

            answer = bot.answer(user_input)
            print(f"\n🤖 Ответ: {answer}")

        except KeyboardInterrupt:
            print("\nДо свидания!")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()