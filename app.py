from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

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
        # Обрабатываем загруженный файл
        original_pdf = PdfReader(file)

        # Создаем PDF с оглавлением на второй странице
        output = PdfWriter()
        output.add_page(original_pdf.pages[0])  # Первая страница оригинального файла

        # Создание второй страницы с оглавлением
        buffer = io.BytesIO()
        can = canvas.Canvas(buffer, pagesize=letter)
        can.drawString(100, 750, "Table of Contents")
        can.drawString(100, 720, "1. Introduction - Page 1")
        can.drawString(100, 690, "2. Second Chapter - Page 2")
        can.showPage()
        can.save()

        buffer.seek(0)
        toc_pdf = PdfReader(buffer)
        output.add_page(toc_pdf.pages[0])  # Добавляем страницу с оглавлением

        # Добавляем остальные страницы из оригинала
        for page_num in range(1, len(original_pdf.pages)):
            output.add_page(original_pdf.pages[page_num])

        # Создаем новый PDF файл
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
