# AI_Service/ai_service.py
import os
import cv2
import numpy as np
import requests
from flask import Flask, request, jsonify
from ultralytics import YOLO

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  

BACKEND_URL = "http://127.0.0.1:5000/save-result"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "best.pt")
MOCK_PATH = os.path.join(CURRENT_DIR, "runs", "detect", "train", "weights", "best.pt")

print("=" * 60)
print("[HỆ THỐNG AI] Đang khởi tạo mô hình nhận diện OBJECT DETECTION...")

ACTIVE_MODEL_PATH = MODEL_PATH if os.path.exists(MODEL_PATH) else MOCK_PATH if os.path.exists(MOCK_PATH) else None

if not ACTIVE_MODEL_PATH:
    print("\n" + "!" * 60)
    print("[LỖI NGHIÊM TRỌNG] Không tìm thấy bất kỳ file 'best.pt' nào!")
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
        file = request.files['image']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Dữ liệu ảnh truyền sang bị hỏng, không thể giải mã!"}), 400

        # 2. ĐƯA ẢNH VÀO MÔ HÌNH DỰ ĐOÁN
        results = model(frame) 
        result = results[0]
        
        # Mặc định ban đầu
        class_index = -1
        confidence = 0.0
        box_coords = [] # Mảng chứa tọa độ [x1, y1, x2, y2] để trả về UI vẽ khung

        # 3. BÓC TÁCH KẾT QUẢ VÀ LẤY TỌA ĐỘ KHUNG BẰNG XYXY
        if hasattr(result, 'boxes') and result.boxes is not None and len(result.boxes) > 0:
            class_index = int(result.boxes.cls[0])
            confidence = float(result.boxes.conf[0])
            
            # Lấy tọa độ khung vật thể đầu tiên (ép về kiểu int cho OpenCV vẽ dễ)
            coords = result.boxes.xyxy[0].tolist()
            box_coords = [int(c) for c in coords] # [xmin, ymin, xmax, ymax]

        if class_index != -1 and class_index in model.names:
            raw_label = model.names[class_index].lower()
        else:
            raw_label = "unknown"

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

        print(f"[AI SERVICE] Object Detection -> Nhãn gốc: '{raw_label}' | Nhãn dịch: '{label}' | Tọa độ khung: {box_coords}")

        # 4. Gửi kết quả sang Backend để lưu Database
        result_data = {
            "label": label,
            "confidence": str(confidence)
        }
        try:
            requests.post(BACKEND_URL, json=result_data, timeout=3)
        except Exception:
            print(f"[CẢNH BÁO KẾT NỐI] Không lưu được vào Database.")

        # 5. Trả kết quả kèm mảng tọa độ 'box' về cho giao diện vẽ khung
        return jsonify({
            "status": "success", 
            "label": label, 
            "confidence": f"{confidence*100:.2f}%",
            "box": box_coords # Trả thêm trường này sang giao diện
        }), 200

    except Exception as e:
        print(f"[LỖI HỆ THỐNG CRASH]: {str(e)}")
        return jsonify({"status": "error", "message": f"Lỗi xử lý nội bộ AI: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)