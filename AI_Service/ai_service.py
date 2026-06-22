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
print("[HỆ THỐNG AI - TH2] Đang khởi tạo mô hình nhận diện BÓC TÁCH ĐỘC LẬP...")

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
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy dữ liệu túi file mang tên 'image' trong Request!"}), 400
    
    try:
        file = request.files['image']
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Dữ liệu ảnh truyền sang bị hỏng!"}), 400

        # 1. Quét ảnh MỘT LẦN DUY NHẤT để tránh nhận diện lặp
        results = model(frame) 
        result = results[0]
        
        detected_items = []

        # 2. VÒNG LẶP: Xử lý TỪNG VẬT THỂ một thành các dòng dữ liệu riêng
        if hasattr(result, 'boxes') and result.boxes is not None:
            for i in range(len(result.boxes)):
                class_index = int(result.boxes.cls[i])
                confidence = float(result.boxes.conf[i])
                coords = result.boxes.xyxy[i].tolist()
                box_coords = [int(c) for c in coords] 
                
                if class_index in model.names:
                    raw_label = model.names[class_index].lower()
                else:
                    raw_label = "unknown"

                box_color = (128, 128, 128) 
                
                if "inorganic" in raw_label or "vo_co" in raw_label:
                    label = "Rác vô cơ"
                    box_color = (255, 0, 0)      
                elif "organic" in raw_label or "huu_co" in raw_label:
                    label = "Rác hữu cơ"
                    box_color = (0, 255, 0)      
                elif "recycl" in raw_label or "tai_che" in raw_label:
                    label = "Rác tái chế"
                    box_color = (0, 191, 255)    
                elif "hazard" in raw_label or "doc_hai" in raw_label:
                    label = "Rác độc hại"
                    box_color = (0, 0, 255)      
                else:
                    label = "Không nhận diện được"

                if label != "Không nhận diện được":
                    # TẠO ẢNH RIÊNG CHO VẬT THỂ HIỆN TẠI
                    # Copy từ frame gốc để ảnh không bị dính khung của các vật thể trước đó
                    single_item_frame = frame.copy()
                    
                    # Vẽ đúng 1 khung bao cho vật thể này
                    cv2.rectangle(single_item_frame, (box_coords[0], box_coords[1]), (box_coords[2], box_coords[3]), box_color, 3)

                    # Đóng gói ảnh của vật thể này
                    _, img_encoded = cv2.imencode('.jpg', single_item_frame)
                    img_bytes = img_encoded.tobytes()

                    # Gửi API độc lập xuống Backend (Tạo thành 1 dòng riêng trong Database)
                    files = {'image': (f'detected_item_{i}.jpg', img_bytes, 'image/jpeg')}
                    payload = {'label': label, 'confidence': f"{confidence * 100:.2f}%"}
                    
                    try:
                        requests.post(BACKEND_URL, data=payload, files=files, timeout=4)
                        print(f"[AI SERVICE] Đã tách & lưu dòng riêng: {label} ({confidence * 100:.2f}%)")
                    except Exception as e:
                        print(f"[CẢNH BÁO KẾT NỐI] Không gửi vật thể {i} sang Backend được: {e}")

                    # Ghi nhận vào mảng chung
                    detected_items.append({
                        "label": label,
                        "confidence": f"{confidence * 100:.2f}%",
                        "box": box_coords
                    })

        # 3. Trả thông báo tóm tắt về cho Giao diện UI
        if len(detected_items) > 0:
            # Gom các nhãn lại để UI hiển thị cho đẹp (VD: Rác tái chế, Rác vô cơ)
            unique_labels = list(set([item["label"] for item in detected_items]))
            ui_label = ", ".join(unique_labels)
            
            # Thông báo cho UI biết đã tách bao nhiêu dòng
            ui_conf = f"Đã tách {len(detected_items)} dòng dữ liệu"

            return jsonify({
                "status": "success", 
                "items": detected_items, 
                "label": ui_label,     
                "confidence": ui_conf, 
                "box": detected_items[0]["box"] 
            }), 200
        else:
            return jsonify({"status": "success", "label": "Không nhận diện được"}), 200

    except Exception as e:
        print(f"[LỖI HỆ THỐNG CRASH]: {str(e)}")
        return jsonify({"status": "error", "message": f"Lỗi xử lý nội bộ AI: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)