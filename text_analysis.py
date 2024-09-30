import re


# Пример функции для добавления оглавления на основе анализа текста
def add_toc_annotations(text):
    toc = []
    annotated_text = ""

    # Простая логика для добавления заголовков и аннотаций
    for line in text.split('\n'):
        if re.match(r'^\d+\.', line):  # Пример заголовков вида "1.", "2.", etc.
            toc.append(line.strip())  # Добавляем в оглавление
            annotated_text += f"[TOC] {line.strip()}\n"  # Добавляем пометку оглавления
        else:
            annotated_text += line + "\n"

    # Добавляем оглавление в начало текста
    if toc:
        annotated_text = "Оглавление:\n" + "\n".join(toc) + "\n\n" + annotated_text

    return annotated_text
