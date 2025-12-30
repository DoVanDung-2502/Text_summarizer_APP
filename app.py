
import google.generativeai as genai
import os
import logging
import hashlib
from werkzeug.utils import secure_filename
from flask_caching import Cache 
from flask import Flask,render_template,request
from pdf_process import summarize_pdf
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
app = Flask(__name__)

# ---------------------------------------
# Cấu hình Logging (Nhật ký)
# ---------------------------------------
logging.basicConfig(
    filename='app.log',
    level = logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ---------------------------------------
# Cấu hình Cache (Bộ nhớ đệm)
# ---------------------------------------
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CaCHE_DEFAULT_TIMEOUT': 300})

# ---------------------------------------
# Cấu hình API AI
# ---------------------------------------

load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", # Dùng model chuẩn 1.5-flash
    temperature=0.5
)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------------------------------
# Tạo mã duy nhất cho đoạn văn
# ---------------------------------------
def generate_cache_key(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

@app.route("/", methods=["GET", "POST"])


def home():
    summary_result = ""
    original_text = ""
    error_msg = ""
    
    if request.method == "POST":
        try:
            # Upload file PDF
            if 'input_file' in request.files and request.files['input_file'].filename != '':
                file = request.files['input_file']
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                logging.info(f"User Uploading file: {filename}")
                file.save(file_path)
                summary_result = summarize_pdf(file_path)
                os.remove(file_path)  # Xoá file sau khi tóm tắt
                logging.info(f"File {filename} summarized successfully.")
            elif 'input_text' in request.form and request.form['input_text'].strip() != '':
                original_text = request.form['input_text']
                cache_key = generate_cache_key(original_text)
                cached_data = cache.get(cache_key)
                
                if cached_data:
                    logging.info("HIT CACHE! Kêt quả được lấy từ bộ nhớ đệm.")
                    summary_result = cached_data + " (Lấy từ bộ nhớ đệm)"
                else:
                    logging.info("MISS CACHE! Gọi AI để tạo tóm tắt.")
                    prompt = f"Hãy tóm tắt văn bản sau một cách ngắn gọn và súc tích bằng tiếng việt. {original_text}"
                    response = llm.invoke(prompt)
                    summary_result = response.text
                    
                    cache.set(cache_key, summary_result) # Lưu kêt quả vào bộ nhớ đệm dùng cho lần sau
            else:
                error_msg = "Vui lòng nhập văn bản hoặc tải lên file PDF."
        except Exception as e:
            logging.error(f"Lỗi xảy ra: {str(e)}")
            error_msg = (f"Lỗi xảy ra với hệ thống. Vui lòng thử lại sau. Chi tiết lỗi: {str(e)}")
    
    return render_template(
        "index.html",
        summary=summary_result,
        original_text=original_text,
        error_msg=error_msg
    )

    
    
if __name__ == "__main__":
    app.run(debug=True)
    