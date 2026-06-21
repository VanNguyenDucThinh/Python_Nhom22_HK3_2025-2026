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

@app.route('/predict', methods=['POST'])
def process_image():
    """API nhận ảnh từ Giao diện, đưa cho YOLO Detect, tự vẽ box màu theo loại rác và ném sang Backend"""
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy dữ liệu túi file mang tên 'image' trong Request!"}), 400
    
    try:
        file = request.files['image']
        # Dùng np.frombuffer để đọc mảng byte ổn định hơn
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Dữ liệu ảnh truyền sang bị hỏng, không thể giải mã!"}), 400

        # 1. Đưa ảnh vào mô hình dự đoán
        results = model(frame) 
        result = results[0]
        
        class_index = -1
        confidence = 0.0
        box_coords = []

        # 2. Bóc tách kết quả vật thể đầu tiên tìm thấy
        if hasattr(result, 'boxes') and result.boxes is not None and len(result.boxes) > 0:
            class_index = int(result.boxes.cls[0])
            confidence = float(result.boxes.conf[0])
            coords = result.boxes.xyxy[0].tolist()
            box_coords = [int(c) for c in coords] # [xmin, ymin, xmax, ymax]

        if class_index != -1 and class_index in model.names:
            raw_label = model.names[class_index].lower()
        else:
            raw_label = "unknown"

        # Định nghĩa ánh xạ màu sắc BGR (OpenCV sử dụng Blue - Green - Red)
        # Mặc định là màu xám nếu không khớp loại
        box_color = (128, 128, 128) 

        # Phân loại nhãn tiếng Việt và gán màu sắc đồng bộ với Giao diện
        if "inorganic" in raw_label or "vo_co" in raw_label:
            label = "Rác vô cơ"
            box_color = (255, 0, 0)      # Xanh dương (B=255, G=0, R=0)
        elif "organic" in raw_label or "huu_co" in raw_label:
            label = "Rác hữu cơ"
            box_color = (0, 255, 0)      # Xanh lá (B=0, G=255, R=0)
        elif "recycl" in raw_label or "tai_che" in raw_label:
            label = "Rác tái chế"
            box_color = (0, 191, 255)    # Vàng/Cam sáng (B=0, G=191, R=255)
        elif "hazard" in raw_label or "doc_hai" in raw_label:
            label = "Rác độc hại"
            box_color = (0, 0, 255)      # Đỏ (B=0, G=0, R=255)
        else:
            label = "Không nhận diện được"

        conf_str = f"{confidence * 100:.2f}%"
        print(f"[AI SERVICE] Nhãn gốc: '{raw_label}' | Nhãn dịch: '{label}' | Khung: {box_coords}")

        # 3. Tiến hành gửi kết quả và ẢNH THỰC TẾ sang Backend lưu trữ (Nếu nhận diện thành công)
        if label != "Không nhận diện được":
            frame_to_save = frame.copy()
            if len(box_coords) == 4:
                # 🔥 ĐÃ SỬA: Chỉ vẽ bounding box với độ dày nét = 3, KHÔNG vẽ chữ lên ảnh
                cv2.rectangle(frame_to_save, (box_coords[0], box_coords[1]), (box_coords[2], box_coords[3]), box_color, 3)
            
            # Chuyển đổi ảnh đã vẽ khung màu thành chuỗi bytes định dạng .jpg
            _, img_encoded = cv2.imencode('.jpg', frame_to_save)
            img_bytes = img_encoded.tobytes()

            # Đóng gói Multipart gửi sang Backend
            files = {
                'image': ('detected_waste.jpg', img_bytes, 'image/jpeg')
            }
            payload = {
                'label': label,
                'confidence': conf_str
            }
            
            try:
                requests.post(BACKEND_URL, data=payload, files=files, timeout=4)
            except Exception as e:
                print(f"[CẢNH BÁO KẾT NỐI] Không gửi ảnh và dữ liệu sang Backend lưu được: {e}")

        # 4. Trả kết quả về cho Giao diện hiển thị trực tiếp
        return jsonify({
            "status": "success", 
            "label": label, 
            "confidence": conf_str,
            "box": box_coords
        }), 200

    except Exception as e:
        print(f"[LỖI HỆ THỐNG CRASH]: {str(e)}")
        return jsonify({"status": "error", "message": f"Lỗi xử lý nội bộ AI: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)