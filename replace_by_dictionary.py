import json
import os
import re

def replace_terms_in_files(folder_path, terms_map):
    terms_pattern = re.compile(
        r'\b(' + '|'.join(map(re.escape, terms_map.keys())) + r')(?:\'s|s|es)?\b',
        flags=re.IGNORECASE
    )

    filename_terms_pattern = re.compile(
        r'\b(' + '|'.join(map(re.escape, terms_map.keys())) + r')(?:\'s|s|es)?\b',
        flags=re.IGNORECASE
    )

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            def replacer(match):
                matched_word = match.group(0)
                suffix = ''
                base_word = matched_word

                if matched_word.lower().endswith("'s"):
                    suffix = "'s"
                    base_word = matched_word[:-2]
                elif matched_word.lower().endswith("es"):
                    base_without_es = matched_word[:-2]
                    if base_without_es.lower() in [term.lower() for term in terms_map.keys()]:
                        suffix = "es"
                        base_word = base_without_es
                    else:
                        base_word = matched_word
                elif matched_word.lower().endswith("s"):
                    base_without_s = matched_word[:-1]
                    if base_without_s.lower() in [term.lower() for term in terms_map.keys()]:
                        suffix = "s"
                        base_word = base_without_s
                    else:
                        base_word = matched_word

                for term, new_term in terms_map.items():
                    if term.lower() == base_word.lower():
                        return new_term + suffix
                return matched_word

            new_content = terms_pattern.sub(replacer, content)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Обработан файл: {filename}")

        def filename_replacer(match):
            matched_word = match.group(0)
            suffix = ''
            base_word = matched_word

            if matched_word.lower().endswith("'s"):
                suffix = "'s"
                base_word = matched_word[:-2]
            elif matched_word.lower().endswith("es"):
                base_without_es = matched_word[:-2]
                if base_without_es.lower() in [term.lower() for term in terms_map.keys()]:
                    suffix = "es"
                    base_word = base_without_es
                else:
                    base_word = matched_word
            elif matched_word.lower().endswith("s"):
                base_without_s = matched_word[:-1]
                if base_without_s.lower() in [term.lower() for term in terms_map.keys()]:
                    suffix = "s"
                    base_word = base_without_s
                else:
                    base_word = matched_word

            for term, new_term in terms_map.items():
                if term.lower() == base_word.lower():
                    return new_term + suffix
            return matched_word

        new_filename = filename_terms_pattern.sub(filename_replacer, filename)

        if new_filename != filename:
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            os.rename(old_file_path, new_file_path)
            print(f"Переименован файл: {filename} -> {new_filename}")

def main():
    folder_path = "knowledge_base"
    terms_map_path = os.path.join("terms.json")

    with open(terms_map_path, 'r', encoding='utf-8') as file:
        terms_map = json.load(file)

    replace_terms_in_files(folder_path, terms_map)
    print("Замены выполнены успешно!")

if __name__ == "__main__":
    main()
