from flask import Flask, render_template, request, send_file, redirect, flash
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Импортируем функции из других файлов
from extract_text import extract_text_from_pdf
from text_analysis import generate_table_of_contents

app = Flask(__name__)


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
        # Шаг 1: Извлекаем текст из загруженного PDF
        text_list = extract_text_from_pdf(file)

        # Шаг 2: Генерируем оглавление на основе извлечённого текста
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
        can.drawString(100, 750, "Table of Contents")

        # Добавляем оглавление в PDF
        y_position = 720
        for entry in toc:
            can.drawString(100, y_position, entry)
            y_position -= 30  # Сдвигаем текст вниз на каждой строке

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

        # Возвращаем новый файл пользователю
        return send_file(result_pdf, as_attachment=True, download_name="modified_pdf_with_toc.pdf")
    else:
        flash('File is not a PDF')
        return redirect(request.url)


if __name__ == '__main__':
    app.run(debug=True)
