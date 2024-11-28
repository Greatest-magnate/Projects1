import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from reportlab.lib.pagesize import letter
from reportlab.pdfgen import canvas
import csv
import json


invoice = Flask(__name__)
invoice.config['UPLOAD_FOLDER'] = 'uploads'
invoice.config['GENERATED_FOLDER'] = 'generated_invoices'
invoice.config['SECRET_KEY'] = 'your_secret_key'

os.makedirs(invoice.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(invoice.config['GENERATED_FOLDER'], exist_ok=True)


@invoice.route('/')
def index():
    return render_template('index.html')

@invoice.route('/generate', methods=['POST'])
def generate_invoice():
   
    invoice_data = {
        "invoice_number": request.form.get("invoice_number"),
        "customer_name": request.form.get("customer_name"),
        "date": request.form.get("date"),
        "items": []
    }
 
    for i in range(int(request.form.get("item_count", 0))):
        item = {
            "description": request.form.get(f"description_{i}"),
            "quantity": request.form.get(f"quantity_{i}"),
            "price": request.form.get(f"price_{i}"),
        }
        if item["description"]:
            invoice_data["items"].append(item)


    pdf_filename = f"Invoice_{invoice_data['invoice_number']}.pdf"
    pdf_path = os.path.join(invoice.config['GENERATED_FOLDER'], pdf_filename)
    create_pdf(invoice_data, pdf_path)

    return send_file(pdf_path, as_attachment=True)

@invoice.route('/upload', methods=['POST'])
def upload_data():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(invoice.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
       
        invoice_data = parse_file(file_path)
        if invoice_data:
            pdf_filename = f"Invoice_{invoice_data['invoice_number']}.pdf"
            pdf_path = os.path.join(invoice.config['GENERATED_FOLDER'], pdf_filename)
            create_pdf(invoice_data, pdf_path)
            return send_file(pdf_path, as_attachment=True)

    flash('Invalid file or format. Please upload a CSV or JSON file.')
    return redirect(url_for('index'))

def create_pdf(data, path):
    
    pdf = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, f"Invoice #{data['invoice_number']}")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 80, f"Customer: {data['customer_name']}")
    pdf.drawString(50, height - 100, f"Date: {data['date']}")

  
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 140, "Description")
    pdf.drawString(300, height - 140, "Quantity")
    pdf.drawString(400, height - 140, "Price")


    y = height - 160
    total = 0
    for item in data["items"]:
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, y, item["description"])
        pdf.drawString(300, y, item["quantity"])
        pdf.drawString(400, y, f"${item['price']}")
        total += float(item["quantity"]) * float(item["price"])
        y -= 20

 
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y - 20, f"Total: ${total:.2f}")

    pdf.save()

def parse_file(path):
   
    invoice_data = {"items": []}
    if path.endswith(".csv"):
        with open(path, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            invoice_data["invoice_number"] = "Uploaded_CSV"
            for row in reader:
                invoice_data["items"].append(row)
    elif path.endswith(".json"):
        with open(path, mode="r") as jsonfile:
            invoice_data = json.load(jsonfile)
    return invoice_data

if __name__ == '__main__':
    invoice.run(debug=True)