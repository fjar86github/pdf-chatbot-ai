import streamlit as st
import requests

# Judul Aplikasi
st.title("Chatbot AI PDF Processor")

# Upload PDF
pdf_file = st.file_uploader("Upload PDF", type="pdf")
if pdf_file:
    # Mengirim PDF ke backend untuk ekstraksi teks
    response = requests.post("http://127.0.0.1:5000/upload_pdf", files={"file": pdf_file})
    if response.status_code == 200:
        st.write("Teks dari PDF:")
        st.text_area("Extracted Text", response.json()['text'], height=300)

# Input Pesan untuk Chat
user_message = st.text_input("Ask me anything:")
user_id = "user_123"  # ID pengguna yang tetap untuk percakapan

if user_message:
    # Mengirim pesan ke backend untuk mendapatkan respons
    response = requests.post("http://127.0.0.1:5000/chat", json={"user_id": user_id, "message": user_message})
    if response.status_code == 200:
        st.write("AI Response:", response.json()['response'])
