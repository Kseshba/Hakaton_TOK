from flask import Flask, render_template, request, send_file, redirect, flash
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io

# Импортируем функции из других файлов
from extract_text import extract_titles_from_pdf
from text_analysis import generate_table_of_contents
from extract_text import normalize_text

app = Flask(__name__)

import fitz

def get_rect_coordinates(doc, pages_mas):
    #doc = fitz.open(input_path)
    rect_mas=[]
    link_mas=[]
    c=0
    for i in range(len(pages_mas)):
      rect_mas1=[]
      link_mas1=[]
      page= doc[pages_mas[i]]
      text = page.get_text().split('\n')
      for line in text:
        line=line.strip()
        if len(line)>3 and line[-1].isdigit() and 'из' not in line[-5:]:
           number = line[-5:].strip(' ,.;-:')
           coords = page.search_for(line, quads=False)[-1]
           rect_mas1.append(coords)
           link_mas1.append(number)
      c+=1
      rect_mas.append(rect_mas1)
      link_mas.append(link_mas1)
    print(link_mas)
    return link_mas, rect_mas




def make_interactive_toc(doc, link_mas, rect_mas, pages_mas):
    for i in range(len(pages_mas)):
        page_num = pages_mas[i]
        current_page = doc[page_num]
        for j in range(len(link_mas[i])):
            target_page = int(link_mas[i][j]) - 1  # Целевая страница
            print(f"Creating link from page {page_num} to page {target_page}")
            # Пример корректного использования insert_link
            rect = fitz.Rect(50, 50, 100, 100)  # Определение координат области
            current_page.insert_link({
                "kind": 5,
                "from": rect,  # Здесь должен быть объект Rect
                "page": int(link_mas[i][j]) - 2,
                "to": int(link_mas[i][j]) - 2,
                "file": "",
                "xref": ""
            })
    return doc


@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['pdf_file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and file.filename.endswith('.pdf'):
        # Шаг 2: Генерируем оглавление на основе извлечённого текста
        text_list = extract_titles_from_pdf(file)
        toc = generate_table_of_contents(text_list)

        # Шаг 3: Создаём PDF с оглавлением на второй странице
        file.seek(0)  # Возвращаем указатель к началу файла
        original_pdf = PdfReader(file)

        # Создаём новый PDF-документ
        output = PdfWriter()
        output.add_page(original_pdf.pages[0])  # Первая страница оригинального PDF

        # Создание второй страницы с оглавлением
        buffer = io.BytesIO()
        can = canvas.Canvas(buffer, pagesize=letter)

        # Регистрация шрифта DejaVuSans
        font_path = "DejaVuSans.ttf"  # Укажи правильный путь к шрифту
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))

        # Использование шрифта DejaVuSans
        can.setFont("DejaVu", 12)

        can.drawString(100, 750, "Table of Contents")

        # Добавляем оглавление в PDF
        y_position = 720
        for entry in toc:
            can.drawString(100, y_position, normalize_text(str(entry)))
            y_position -= 30  # Сдвигаем текст вниз на каждой строке
            if y_position < 100:  # Если текст выходит за пределы страницы
                can.showPage()  # Добавляем новую страницу
                can.setFont("DejaVu", 12)  # Переустанавливаем шрифт

        can.showPage()
        can.save()

        buffer.seek(0)
        toc_pdf = PdfReader(buffer)
        output.add_page(toc_pdf.pages[0])  # Добавляем страницу с оглавлением

        # Добавляем остальные страницы из оригинала
        for page_num in range(1, len(original_pdf.pages)):
            output.add_page(original_pdf.pages[page_num])

        # Создаём новый PDF файл
        result_pdf = io.BytesIO()
        output.write(result_pdf)
        result_pdf.seek(0)

        # Открываем поток BytesIO как PDF с помощью fitz
        input_pdf = fitz.open(stream=result_pdf, filetype="pdf")

        # Пример работы с номерами страниц
        pages_mas = [1]  # Укажи правильные номера страниц
        link_mas, rect_mas = get_rect_coordinates(input_pdf, pages_mas)

        # Применяем оглавление с ссылками
        output_pdf = make_interactive_toc(input_pdf, link_mas, rect_mas, pages_mas)

        # Сохраняем изменения в BytesIO
        output_bytes = io.BytesIO()
        output_pdf.save(output_bytes)
        output_bytes.seek(0)

        # Возвращаем изменённый PDF с оглавлением
        return send_file(output_bytes, as_attachment=True, download_name="modified_pdf_with_toc.pdf")
    else:
        flash('File is not a PDF')
        return redirect(request.url)


if __name__ == '__main__':
    app.run(debug=True)



