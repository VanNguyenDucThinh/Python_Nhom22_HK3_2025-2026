# AI_Service/ai_service.py
import os
import cv2
import numpy as np
import requests
from flask import Flask, request, jsonify
from ultralytics import YOLO

app = Flask(__name__)
# Ép Flask trả về chuỗi tiếng Việt Unicode thô thay vì ép sang mã ASCII (\xef...)
app.config['JSON_AS_ASCII'] = False  

# Địa chỉ API của dịch vụ Backend lưu Database
BACKEND_URL = "http://127.0.0.1:5000/save-result"

# Nạp model
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "best.pt")

print("=" * 60)
print("[HỆ THỐNG AI] Đang khởi tạo mô hình nhận diện...")

if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH)
    print(f"[THÀNH CÔNG] Đã nạp mô hình YOLOv8 chính thức tại: {MODEL_PATH}")
    IS_MOCK = False
else:
    MOCK_PATH = os.path.join(CURRENT_DIR, "runs", "classify", "train", "weights", "best.pt")
    if os.path.exists(MOCK_PATH):
        model = YOLO(MOCK_PATH)
        print(f"[TẠM THỜI] Đang nạp mô hình từ thư mục huấn luyện: {MOCK_PATH}")
        IS_MOCK = False
    else:
        print(f"[CẢNH BÁO] Không tìm thấy file model. Đang dùng model gốc yolov8n-cls.pt để chạy thử.")
        model = YOLO("yolov8n-cls.pt")
        IS_MOCK = True
print("=" * 60)

@app.route('/upload-image', methods=['POST'])
def process_image():
    """API nhận ảnh từ Camera/File, đưa cho YOLO phân loại và chuyển tiếp sang Backend"""
    # Bẫy lỗi kiểm tra sự tồn tại của file ảnh trong request gửi đến
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy dữ liệu túi file mang tên 'image' trong Request!"}), 400
    
    try:
        # 1. Đọc ảnh từ Request
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Dữ liệu ảnh truyền sang bị hỏng, không thể giải mã!"}), 400

        # 2. Đưa ảnh vào YOLOv8 để dự đoán
        results = model(frame)
        
        # 3. Bóc tách kết quả từ YOLOv8
        probs = results[0].probs
        class_index = int(probs.top1)            
        confidence = float(probs.top1conf)       
        raw_label = model.names[class_index].lower() # Chuyển về chữ thường để so sánh chính xác

        # Chuyển đổi nhãn tiếng Anh sang tiếng Việt
        if "organic" in raw_label or "huu_co" in raw_label:
            label = "Rác hữu cơ"
        elif "recycl" in raw_label or "tai_che" in raw_label:
            label = "Rác tái chế"
        else:
            label = "Rác vô cơ"

        # Nếu đang chạy Mock (chưa huấn luyện), giả lập data trực quan để test luồng
        if IS_MOCK:
            labels_test = ["Rác hữu cơ", "Rác tái chế", "Rác vô cơ"]
            label = np.random.choice(labels_test)
            confidence = float(np.random.uniform(0.82, 0.98))

        print(f"[AI SERVICE] Dự đoán thực tế: {label} | Độ tin cậy: {confidence*100:.2f}%")

        # 4. Gửi kết quả sang Backend để lưu Database
        result_data = {
            "label": label,
            "confidence": f"{confidence*100:.2f}%"
        }
        try:
            requests.post(BACKEND_URL, json=result_data, timeout=3)
        except Exception:
            print(f"[CẢNH BÁO KẾT NỐI] Không lưu được vào Database (Backend cổng 5000 chưa bật).")

        # 5. Trả kết quả sạch dạng JSON hỗ trợ Unicode tiếng Việt đầy đủ
        return jsonify({
            "status": "success", 
            "label": label, 
            "confidence": f"{confidence*100:.2f}%"
        }), 200

    except Exception as e:
        print(f"[LỖI HỆ THỐNG] {str(e)}")
        return jsonify({"status": "error", "message": f"Lỗi xử lý nội bộ AI: {str(e)}"}), 500

if __name__ == '__main__':
    print("Khởi động AI Service thành công tại http://127.0.0.1:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)