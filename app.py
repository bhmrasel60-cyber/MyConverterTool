import os
import fitz  # PyMuPDF
import qrcode
from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import zipfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# ১. PDF to Image (সব পেজ জিপ ফাইল হিসেবে দেবে)
@app.route('/pdf-to-img', methods=['POST'])
def pdf_to_img():
    file = request.files['pdf_file']
    if file:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(len(doc)):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                zip_file.writestr(f"page_{i+1}.png", img_data)
        doc.close()
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='pdf_images.zip')

# ২. Split PDF
@app.route('/split-pdf', methods=['POST'])
def split_pdf():
    file = request.files['pdf_file']
    start = int(request.form.get('start')) - 1
    end = int(request.form.get('end'))
    if file:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start, to_page=end-1)
        pdf_io = io.BytesIO()
        new_doc.save(pdf_io)
        pdf_io.seek(0)
        return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='split.pdf')

# ৩. QR Code Maker
@app.route('/generate-qr', methods=['POST'])
def generate_qr():
    data = request.form.get('qr_text')
    img = qrcode.make(data)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='qrcode.png')

# ৪. Job Photo (300x300)
@app.route('/convert-job-photo', methods=['POST'])
def job_photo():
    file = request.files['image']
    if file:
        img = Image.open(file).convert("RGB").resize((300, 300))
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='job_photo.jpg')

# ৫. Signature (300x80)
@app.route('/convert-signature', methods=['POST'])
def convert_signature():
    file = request.files['image']
    if file:
        img = Image.open(file).convert("RGB").resize((300, 80))
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='signature.jpg')

# ৬. PDF Merger
@app.route('/merge-pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('files')
    result_pdf = fitz.open()
    for file in files:
        curr_pdf = fitz.open(stream=file.read(), filetype="pdf")
        result_pdf.insert_pdf(curr_pdf)
    pdf_io = io.BytesIO()
    result_pdf.save(pdf_io)
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='merged.pdf')

# ৭. Image to PDF
@app.route('/img-to-pdf', methods=['POST'])
def img_to_pdf():
    files = request.files.getlist('images')
    pdf_bytes = fitz.open().tobytes()
    pdf_doc = fitz.open("pdf", pdf_bytes)
    for file in files:
        img = Image.open(file).convert("RGB")
        img_io = io.BytesIO()
        img.save(img_io, format="PDF")
        img_pdf = fitz.open("pdf", img_io.getvalue())
        pdf_doc.insert_pdf(img_pdf)
    pdf_final = io.BytesIO()
    pdf_doc.save(pdf_final)
    pdf_final.seek(0)
    return send_file(pdf_final, mimetype='application/pdf', as_attachment=True, download_name='images.pdf')

# ৮. PDF to Text
@app.route('/pdf-to-text', methods=['POST'])
def pdf_to_text():
    file = request.files['pdf_file']
    if file:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = "".join([page.get_text() for page in doc])
        return send_file(io.BytesIO(text.encode()), mimetype='text/plain', as_attachment=True, download_name='text.txt')

# ৯. JPG to PNG
@app.route('/jpg-to-png', methods=['POST'])
def jpg_to_png():
    file = request.files['image']
    if file:
        img = Image.open(file)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='converted.png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)