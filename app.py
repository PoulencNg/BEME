import os
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from openai import OpenAI
from docx import Document

# Load environment variables
load_dotenv()

# Check and set OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key. Please set OPENAI_API_KEY in the environment variables.")

# Configure Flask app
app = Flask(__name__, template_folder='templates')

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'flac', 'm4a', 'aac', 'mp4', 'mov', 'avi', 'mkv', 'amsr', 'ogg'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Email server configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # Email username
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Email password

if not SMTP_USERNAME or not SMTP_PASSWORD:
    raise ValueError("Missing email credentials. Please set SMTP_USERNAME and SMTP_PASSWORD.")

# Check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Convert audio/video to WAV format
def convert_audio(input_path, output_path):
    try:
        processed_output_path = f"{os.path.splitext(output_path)[0]}_processed.wav"
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-ar', '16000',  # Sample rate
            '-ac', '1',      # Mono channel
            '-f', 'wav',
            processed_output_path
        ], check=True)
        return processed_output_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None

# Transcribe audio using OpenAI Whisper API
def transcribe_audio(file_path):
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        with open(file_path, 'rb') as audio_file:
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language="vi"
            )
        return response.get("text", "...")
    except Exception as e:
        print(f"Whisper API error for file {file_path}: {e}")
        return "..."

# Translate text to bilingual format
def translate_bilingual(text):
    if not text or text.strip() == "...":
        return "..."

    prompt = f"""
    Bạn nhận được đầu ra từ Whisper API. Nếu có phần không rõ ràng, hãy thay thế bằng dấu "...". Nhiệm vụ của bạn là:

    1. Chỉnh sửa nội dung để rõ ràng, dễ đọc hơn.
    2. Cắt nhỏ, mỗi đoạn không quá 20 từ.
    3. Dịch nội dung sang tiếng Anh theo định dạng:
       - : <Câu gốc tiếng Việt, nếu không rõ thì giữ nguyên dấu "...">
       -> B : <Bản dịch tiếng Anh, nếu không rõ thì giữ nguyên "...">
    Nội dung: "{text}"
    """
    try:
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia dịch thuật..."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"ChatGPT API error: {e}")
        return "..."

# Export results to Word file
def export_to_word(bilingual_text, output_file):
    try:
        document = Document()
        document.add_heading("Bản Dịch Song Ngữ", level=1)
        document.add_paragraph(bilingual_text)
        document.save(output_file)
        return output_file
    except Exception as e:
        print(f"Error exporting Word file: {e}")
        return None

# Send email with attachment
def send_email_with_attachment(to_email, subject, body, attachment_paths):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        for attachment_path in attachment_paths:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(attachment_path)}'
                )
                msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files or 'email' not in request.form:
        return jsonify({'error': 'Audio file or email not provided.'}), 400

    file = request.files['audio']
    email = request.form['email']
    if file.filename == '' or not email:
        return jsonify({'error': 'No file selected or invalid email.'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        output_filename = f"{os.path.splitext(filename)[0]}.wav"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        converted = convert_audio(input_path, output_path)
        if not converted:
            return jsonify({'error': 'Error converting file format.'}), 500

        transcript = transcribe_audio(converted)
        if not transcript:
            return jsonify({'error': 'Error transcribing audio.'}), 500

        bilingual_text = translate_bilingual(transcript)
        if not bilingual_text:
            return jsonify({'error': 'Error translating text.'}), 500

        word_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(filename)[0]}_result.docx")
        export_to_word(bilingual_text, word_file_path)

        send_email_with_attachment(
            to_email=email,
            subject="Kết quả dịch âm thanh",
            body="Vui lòng kiểm tra file đính kèm để xem kết quả.",
            attachment_paths=[word_file_path]
        )

        try:
            os.remove(input_path)
            os.remove(converted)
        except Exception as e:
            print(f"Error deleting files: {e}")

        return jsonify({'message': 'Results sent to email.', 'bilingual_text': bilingual_text})

    return jsonify({'error': 'Unsupported file format.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
