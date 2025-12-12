from flask import Flask,render_template,request
import google.generativeai as genai
import os

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyB7a-_FFGyg6W-CrpprtoQB-o1ZjQLZ1w8"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def get_summary(text):
    prompt = f"""Hãy toám tắt văn bản sau một cách ngắn gọn và súc tích bằng tiếng việt. Đưa ra ý chính dưới dạng gạch đầu dòng
    Văn bản: {text}"""
    
    try:
        respone = model.generate_content(prompt)
        return respone.text
    except Exception as e:
        return f"Lỗi khi tạo tóm tắt: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def home():
    summary_result = ""
    original_text = ""
    
    if request.method == "POST":
        original_text = request.form["input_text"]
        if original_text:
            summary_result = get_summary(original_text)
    return render_template("index.html", summary=summary_result, original_text=original_text)

if __name__ == "__main__":
    app.run(debug=True)
    