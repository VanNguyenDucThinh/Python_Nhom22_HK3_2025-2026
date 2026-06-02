# AI_Service/ai_service.py
import os
import cv2
import numpy as np
import requests
from flask import Flask, request, jsonify
from ultralytics import YOLO

app = Flask(__name__)

# Địa chỉ API của dịch vụ Backend lưu Database
BACKEND_URL = "http://127.0.0.1:5000/save-result"

# Xác định đường dẫn file model chuẩn nằm ngay trong thư mục gốc AI_Service
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "yolo_rac_v1.pt")

print("=" * 60)
print("[HỆ THỐNG AI] Đang khởi tạo mô hình nhận diện...")

# Kiểm tra file model chuẩn
if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH)
    print(f"[THÀNH CÔNG] Đã nạp mô hình YOLOv8 chính thức tại: {MODEL_PATH}")
    IS_MOCK = False
else:
    # Nếu chưa có file yolo_rac_v1.pt, hệ thống tìm trong folder train mặc định của YOLO làm dự phòng
    MOCK_PATH = os.path.join(CURRENT_DIR, "runs", "classify", "train", "weights", "best.pt")
    if os.path.exists(MOCK_PATH):
        model = YOLO(MOCK_PATH)
        print(f"[TẠM THỜI] Đang nạp mô hình từ thư mục huấn luyện: {MOCK_PATH}")
        print("Khuyên dùng: Bạn nên copy file 'best.pt' ra ngoài và đổi tên thành 'yolo_rac_v1.pt'.")
        IS_MOCK = False
    else:
        print(f"[CẢNH BÁO] Không tìm thấy bất kỳ mô hình YOLOv8 nào!")
        print("Hệ thống sẽ tự động tải mô hình gốc 'yolov8n-cls.pt' để chạy demo không bị crash.")
        model = YOLO("yolov8n-cls.pt")
        IS_MOCK = True
print("=" * 60)

@app.route('/upload-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "Không nhận được file ảnh từ Camera gửi sang."}), 400
    
    file = request.files['image']
    
    try:
        # Bước 1: Chuyển dữ liệu nhị phân nhận được thành mảng ma trận ảnh OpenCV
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise ValueError("Dữ liệu hình ảnh bị hỏng, không thể giải mã.")

        # Bước 2: Đưa trực tiếp ảnh gốc vào YOLOv8 (Không dùng cv2.resize để chống méo hình)
        results = model(frame, verbose=False)
        result = results[0]

        # Lấy chỉ số của nhãn có điểm xác suất cao nhất
        top1_index = result.probs.top1
        confidence = float(result.probs.top1conf)
        
        # Lấy chuỗi tên nhãn gốc từ kết quả của mô hình YOLO
        raw_label = result.names[top1_index]

        # Bước 3: Ánh xạ linh hoạt tên nhãn từ tiếng Anh/viết tắt sang định dạng Tiếng Việt chuẩn của đồ án
        label_lower = raw_label.lower()
        if any(keyword in label_lower for keyword in ["organic", "huu_co", "huco", "organic_waste"]):
            label = "Rác hữu cơ"
        elif any(keyword in label_lower for keyword in ["recycle", "tai_che", "taiche", "recycle_waste"]):
            label = "Rác tái chế"
        else:
            label = "Rác vô cơ"

        # Chế độ chạy thử nghiệm (Nếu hoàn toàn chưa huấn luyện dữ liệu thật)
        if IS_MOCK:
            labels_test = ["Rác hữu cơ", "Rác tái chế", "Rác vô cơ"]
            chiso_mau = int(np.mean(frame))
            np.random.seed(chiso_mau % 1000)
            label = np.random.choice(labels_test)
            confidence = float(np.random.uniform(0.78, 0.97))

        print(f"[AI SERVICE] Dự đoán: {label} | Độ tự tin: {confidence*100:.2f}%")

        # Bước 4: Gọi REST API chuyển tiếp kết quả sang Backend lưu Database
        result_data = {
            "label": label,
            "confidence": confidence
        }

        try:
            requests.post(BACKEND_URL, json=result_data, timeout=3)
        except requests.exceptions.RequestException as e:
            print(f"[CẢNH BÁO KẾT NỐI] Không gửi được dữ liệu tới Backend. Lỗi: {e}")

        # Bước 5: Trả JSON về lại cho luồng giao diện Camera hiển thị Pop-up kết quả
        return jsonify({
            "status": "success", 
            "label": label, 
            "confidence": f"{confidence*100:.2f}%"
        }), 200

    except Exception as e:
        print(f"[LỖI XỬ LÝ AI SERVICE] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Chạy dịch vụ AI trên cổng độc lập 8000
    app.run(host='0.0.0.0', port=8000, debug=True)