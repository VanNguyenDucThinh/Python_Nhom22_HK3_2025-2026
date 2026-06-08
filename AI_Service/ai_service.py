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

if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH)
else:
    print("[LỖI] Không tìm thấy file mô hình best.pt!")

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "Không nhận được file ảnh"}), 400
        
    file = request.files['image']
    file_bytes = np.fromstring(file.read(), np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    try:
        # Chạy dự đoán với mô hình Object Detection
        results = model(frame)
        
        # Mặc định nếu không phát hiện được vật thể nào
        label = "Không nhận diện được"
        confidence = 0.0
        box_coords = []

        # Nếu tìm thấy ít nhất 1 vật thể trong ảnh
        if len(results[0].boxes) > 0:
            first_box = results[0].boxes[0]
            confidence = float(first_box.conf[0])
            class_id = int(first_box.cls[0])
            raw_label = model.names[class_id].lower()
            
            # Lấy tọa độ khung bao [x1, y1, x2, y2]
            box_coords = [int(x) for x in first_box.xyxy[0].tolist()]

            # Ánh xạ nhãn tiếng Việt tương tự bản code cũ ổn định của bạn
            if "organic" in raw_label or "huu_co" in raw_label:
                label = "Rác hữu cơ"
            elif "recycl" in raw_label or "tai_che" in raw_label:
                label = "Rác tái chế"
            elif "hazard" in raw_label or "doc_hai" in raw_label:
                label = "Rác độc hại"
            elif "inorganic" in raw_label or "vo_co" in raw_label:
                label = "Rác vô cơ"

        conf_str = f"{confidence * 100:.2f}%"

        # Gửi kết quả sang Backend lưu Database nếu nhận diện thành công
        if label != "Không nhận diện được":
            result_data = {"label": label, "confidence": conf_str}
            try:
                requests.post(BACKEND_URL, json=result_data, timeout=3)
            except Exception:
                print("[CẢNH BÁO] Không kết nối được Backend để lưu lịch sử.")

        # Trả về kết quả đầy đủ cấu trúc gồm cả nhãn, độ tin cậy và tọa độ box
        return jsonify({
            "status": "success",
            "label": label,
            "confidence": conf_str,
            "box": box_coords
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)