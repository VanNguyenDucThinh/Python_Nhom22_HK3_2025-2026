# ai_service.py
import os
import cv2
import numpy as np
import requests
from flask import Flask, request, jsonify

# Bỏ comment dòng dưới đây khi bạn đã có file model thật (.h5 / .keras) do nhóm train
# import tensorflow as tf 

app = Flask(__name__)

# --- CẤU HÌNH ---
# Địa chỉ Backend sẽ nhận kết quả (Ví dụ Backend dùng cổng 5000)
BACKEND_URL = "http://127.0.0.1:5000/save-result"

# Danh sách nhãn (Labels) rác thải - Cần khớp với lúc train model
LABELS = ["Rác hữu cơ", "Rác tái chế", "Rác nguy hại"]

# --- GIẢ LẬP MODEL (CHỐNG LỖI KHI CHƯA CÓ MODEL THẬT) ---
class MockModel:
    """Lớp này sinh ra kết quả giả lập để bạn test API mà không bị lỗi crash."""
    def predict(self, image_array):
        # Trả về một mảng giả lập tỉ lệ % (ví dụ: 10% Hữu cơ, 85% Tái chế, 5% Nguy hại)
        return np.array([[0.10, 0.85, 0.05]])

# Khởi tạo mô hình giả
model = MockModel()
# Khi có file thật, bạn xóa dòng trên và dùng lệnh này:
# model = tf.keras.models.load_model("model_phan_loai.h5")


@app.route('/upload-image', methods=['POST'])
def process_image():
    """Cổng API nhận ảnh từ Camera Service"""
    # Bước 1: Kiểm tra xem request có chứa file ảnh không
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy file 'image' trong request."}), 400
    
    file = request.files['image']
    
    try:
        # Bước 2: Dùng NumPy chuyển luồng bytes thành mảng dữ liệu (Array)
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise ValueError("Không thể giải mã mảng dữ liệu ảnh.")

        # Định dạng lại ảnh (224x224) để phù hợp với chuẩn đầu vào của mô hình Keras
        frame_resized = cv2.resize(frame, (224, 224))
        
        # Thêm chiều thứ 4 (Batch size = 1) để Keras có thể đọc được -> Shape: (1, 224, 224, 3)
        input_array = np.expand_dims(frame_resized, axis=0)
        
        # (Tùy chọn) Chuẩn hóa pixel về [0, 1] nếu lúc train model nhóm bạn có làm
        # input_array = input_array / 255.0

        # Bước 3: Đưa mảng vào TensorFlow/Keras để dự đoán
        predictions = model.predict(input_array)
        
        # Bóc tách kết quả
        confidence = float(np.max(predictions)) # Lấy xác suất cao nhất
        predicted_class_index = int(np.argmax(predictions)) # Lấy vị trí của xác suất cao nhất
        label = LABELS[predicted_class_index]

        print(f"[AI SERVICE] Kết quả: {label} (Độ tự tin: {confidence*100:.1f}%)")

        result_data = {
            "label": label,
            "confidence": confidence
        }

        # Bước 4: Chuyển tiếp kết quả sang Backend để lưu Database
        try:
            print("[AI SERVICE] Đang gửi dữ liệu sang Backend...")
            backend_response = requests.post(BACKEND_URL, json=result_data, timeout=3)
            backend_response.raise_for_status()
            print("[AI SERVICE] Đã gửi Backend thành công.")
        except requests.exceptions.RequestException as e:
            # Cảnh báo nhưng KHÔNG dừng chương trình, vì bản thân AI đã hoàn thành nhiệm vụ
            print(f"[CẢNH BÁO] Không kết nối được Backend (Có thể chưa bật). Lỗi: {e}")

        # Bước 5: Trả JSON về cho UI (Giao diện) để hiển thị Pop-up
        return jsonify({
            "status": "success", 
            "label": label, 
            "confidence": f"{confidence*100:.2f}%"
        }), 200

    except Exception as e:
        print(f"[LỖI NGHIÊM TRỌNG] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    # Chạy Flask ở cổng 8000 để khớp với API_URL trong config.py của UI
    print("Khởi động AI Service tại http://127.0.0.1:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)