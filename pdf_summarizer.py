import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains  import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# os.environ["GOOGLE_API_KEY"] = "AIzaSyB7a-_FFGyg6W-CrpprtoQB-o1ZjQLZ1w8"
def summarize_pdf(pdf_file_path):
    print("Loading PDF ....")
    
    # Đọc file PDF
    loader = PyPDFLoader(pdf_file_path)
    docs = loader.load_and_split()
    
    # Kiểm tra xem có đọc được trang nào không
    if len(docs) == 0:
        return "Lỗi: Không đọc được nội dung PDF. Có thể file là dạng ảnh (scan) hoặc file rỗng."
        
    print(f"Number of pages in PDF: {len(docs)}")
    
    # Khởi tạo mô hình ngôn ngữ
    # SỬA LỖI Ở ĐÂY: đổi 'model_name' thành 'model' và dùng tên model chuẩn
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", # Dùng model chuẩn 1.5-flash
        temperature=0.5
    )
    
    # Prompt tùy chỉnh (Sửa lại dấu ngoặc kép thừa)
    prompt_template = """
    Bạn là chuyên gia tóm tắt văn bản .
    Hãy viết một bản tóm tắt ngắn gọn, súc tích cho văn bản sau:
    {text}
    
    TÓM TẮT:
    """
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Xử lý chuỗi 
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    
    # Chạy chương trình
    try:
        summary = chain.invoke(docs)
        return summary['output_text']
    except Exception as e:
        return f"Đã xảy ra lỗi khi gọi AI: {str(e)}"

if __name__ == "__main__":
    # Sử dụng raw string (r"...") để tránh lỗi đường dẫn trên Windows
    file_name = r"C:\Day24_Summarizer_app\Dantri.pdf"
    
    if os.path.exists(file_name):
        ket_qua = summarize_pdf(file_name)
        print(f"KẾT QUẢ: {ket_qua}")
    else:
        print(f"File không tồn tại: {file_name}")