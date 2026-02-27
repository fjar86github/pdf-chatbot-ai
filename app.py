import openai
import pdfplumber
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Set API Key OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set Database URI (gunakan SQLite untuk kemudahan)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
db = SQLAlchemy(app)

# Model untuk menyimpan chat history
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)

# Endpoint untuk upload PDF
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    pdf_file = request.files['file']
    pdf_text = extract_text_from_pdf(pdf_file)
    return jsonify({"text": pdf_text})

# Fungsi untuk mengekstrak teks dari PDF
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Endpoint untuk chat dengan AI
@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json['user_id']
    user_message = request.json['message']
    
    # Cari chat history untuk pengguna
    chat_history = ChatHistory.query.filter_by(user_id=user_id).all()
    conversation = "\n".join([f"User: {ch.message}\nAI: {ch.response}" for ch in chat_history])

    # Query ke OpenAI API untuk mendapatkan respons
    prompt = f"Conversation history: {conversation}\nUser: {user_message}\nAI:"
    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        max_tokens=150
    )

    ai_response = response.choices[0].text.strip()

    # Simpan percakapan ke database
    new_chat = ChatHistory(user_id=user_id, message=user_message, response=ai_response)
    db.session.add(new_chat)
    db.session.commit()

    return jsonify({"response": ai_response})

# Run server
if __name__ == '__main__':
    db.create_all()  # Membuat tabel di database
    app.run(debug=True)
