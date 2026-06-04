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

# Nạp model bằng đường dẫn tuyệt đối (Chống lệch thư mục làm việc)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "best.pt")
MOCK_PATH = os.path.join(CURRENT_DIR, "runs", "detect", "train", "weights", "best.pt")

print("=" * 60)
print("[HỆ THỐNG AI] Đang khởi tạo mô hình nhận diện OBJECT DETECTION...")

ACTIVE_MODEL_PATH = MODEL_PATH if os.path.exists(MODEL_PATH) else MOCK_PATH if os.path.exists(MOCK_PATH) else None

if not ACTIVE_MODEL_PATH:
    print("\n" + "!" * 60)
    print("[LỖI NGHIÊM TRỌNG] Không tìm thấy bất kỳ file 'best.pt' nào!")
    print(f"-> Giải pháp: Hãy đảm bảo file 'best.pt' đang nằm tại: {MODEL_PATH}")
    print("!" * 60 + "\n")
    raise FileNotFoundError("Hệ thống bắt buộc phải có file model 'best.pt' để khởi động!")

try:
    model = YOLO(ACTIVE_MODEL_PATH)
    print(f"[THÀNH CÔNG] Đã nạp mô hình YOLOv8 chuẩn xác từ: {ACTIVE_MODEL_PATH}")
except Exception as e:
    print(f"[LỖI CRASH] File 'best.pt' bị lỗi cấu trúc hoặc không thể nạp: {e}")
    raise e
print("=" * 60)

@app.route('/upload-image', methods=['POST'])
def process_image():
    """API nhận ảnh từ Camera/File, đưa cho YOLO Detect và chuyển tiếp sang Backend"""
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy dữ liệu túi file mang tên 'image' trong Request!"}), 400
    
    try:
        # 1. Đọc ảnh từ Request gửi sang (Giữ nguyên hệ màu gốc không đổi sang RGB)
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Dữ liệu ảnh truyền sang bị hỏng, không thể giải mã!"}), 400

        # ============================================================
        # 2. ĐƯA ẢNH VÀO MÔ HÌNH DỰ ĐOÁN (THUẦN DETECT)
        # ============================================================
        results = model(frame) 
        result = results[0]
        
        # ============================================================
        # 3. BÓC TÁCH KẾT QUẢ ĐÃ LỌC SẠCH (CHỈ GIỮ LẠI OBJECT DETECTION)
        # ============================================================
        if hasattr(result, 'boxes') and result.boxes is not None and len(result.boxes) > 0:
            # Lấy vật thể đầu tiên tìm thấy trong ảnh
            class_index = int(result.boxes.cls[0])
            confidence = float(result.boxes.conf[0])
        else:
            class_index = -1
            confidence = 0.0

        if class_index != -1 and class_index in model.names:
            raw_label = model.names[class_index].lower()
        else:
            raw_label = "unknown"

        # ============================================================
        # ĐÃ SỬA: ĐỔI THỨ TỰ ĐỂ TRÁNH BẮT NHẦM CHUỖI CON "ORGANIC"
        # ============================================================
        if "inorganic" in raw_label or "vo_co" in raw_label:
            label = "Rác vô cơ"
        elif "organic" in raw_label or "huu_co" in raw_label:
            label = "Rác hữu cơ"
        elif "recycl" in raw_label or "tai_che" in raw_label:
            label = "Rác tái chế"
        elif "hazard" in raw_label or "doc_hai" in raw_label:
            label = "Rác độc hại"
        else:
            label = "Không nhận diện được"

        print(f"[AI SERVICE] Object Detection -> Nhãn gốc: '{raw_label}' | Nhãn dịch: '{label}' | Độ tin cậy: {confidence*100:.2f}%")

        # 4. Gửi kết quả dạng số thực thuần túy sang Backend để lưu Database (cổng 5000)
        result_data = {
            "label": label,
            "confidence": str(confidence)
        }
        try:
            requests.post(BACKEND_URL, json=result_data, timeout=3)
        except Exception:
            print(f"[CẢNH BÁO KẾT NỐI] Không lưu được vào Database (Backend cổng 5000 chưa bật).")

        # 5. Trả kết quả sạch định dạng phần trăm về cho giao diện hiển thị
        return jsonify({
            "status": "success", 
            "label": label, 
            "confidence": f"{confidence*100:.2f}%"
        }), 200

    except Exception as e:
        print(f"[LỖI HỆ THỐNG CRASH TRONG KHỐI XỬ LÝ DETECT]: {str(e)}")
        return jsonify({"status": "error", "message": f"Lỗi xử lý nội bộ AI: {str(e)}"}), 500

if __name__ == '__main__':
    print("Khởi động AI Service (Object Detection Mode) tại http://127.0.0.1:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)