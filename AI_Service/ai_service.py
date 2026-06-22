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
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"status": "error", "message": "Dữ liệu ảnh truyền sang bị hỏng, không thể giải mã!"}), 400

        # 1. Đưa ảnh vào mô hình dự đoán
        results = model(frame) 
        result = results[0]
        
        detected_items = []
        frame_to_save = frame.copy()

        # 2. Dùng vòng lặp duyệt qua TẤT CẢ các vật thể AI tìm thấy
        if hasattr(result, 'boxes') and result.boxes is not None:
            for i in range(len(result.boxes)):
                class_index = int(result.boxes.cls[i])
                confidence = float(result.boxes.conf[i])
                coords = result.boxes.xyxy[i].tolist()
                box_coords = [int(c) for c in coords] # [xmin, ymin, xmax, ymax]
                
                if class_index in model.names:
                    raw_label = model.names[class_index].lower()
                else:
                    raw_label = "unknown"

                box_color = (128, 128, 128) 
                
                # Phân loại nhãn tiếng Việt và gán màu sắc đồng bộ với Giao diện
                if "inorganic" in raw_label or "vo_co" in raw_label:
                    label = "Rác vô cơ"
                    box_color = (255, 0, 0)      # Xanh dương
                elif "organic" in raw_label or "huu_co" in raw_label:
                    label = "Rác hữu cơ"
                    box_color = (0, 255, 0)      # Xanh lá
                elif "recycl" in raw_label or "tai_che" in raw_label:
                    label = "Rác tái chế"
                    box_color = (0, 191, 255)    # Vàng/Cam sáng
                elif "hazard" in raw_label or "doc_hai" in raw_label:
                    label = "Rác độc hại"
                    box_color = (0, 0, 255)      # Đỏ
                else:
                    label = "Không nhận diện được"

                # Gom dữ liệu các vật thể hợp lệ
                if label != "Không nhận diện được":
                    detected_items.append({
                        "label": label,
                        "raw_conf": confidence, # Giữ số thực để so sánh lấy giá trị lớn nhất
                        "box": box_coords
                    })
                    # Vẽ TẤT CẢ các khung màu lên ảnh
                    cv2.rectangle(frame_to_save, (box_coords[0], box_coords[1]), (box_coords[2], box_coords[3]), box_color, 3)

        # 3. GOM NHÓM DỮ LIỆU CHUẨN KHOA HỌC (Khử trùng & Lấy Max Confidence)
        if len(detected_items) > 0:
            best_detections = {}
            
            # Lọc để giữ lại độ tin cậy CAO NHẤT cho mỗi loại rác
            for item in detected_items:
                lbl = item["label"]
                conf = item["raw_conf"]
                # Nếu nhãn chưa có, hoặc có rồi nhưng độ tin cậy của vật thể này cao hơn -> Cập nhật
                if lbl not in best_detections or conf > best_detections[lbl]:
                    best_detections[lbl] = conf

            # Tạo chuỗi gộp gửi xuống Backend và hiển thị giao diện
            all_labels = ", ".join(best_detections.keys())
            all_confs = ", ".join([f"{conf * 100:.2f}%" for conf in best_detections.values()])
            
            print(f"[AI SERVICE] Nhận diện gộp: {all_labels} (Max Confidence: {all_confs})")

            # Dọn dẹp lại format data trước khi trả về mảng chi tiết
            for item in detected_items:
                item["confidence"] = f"{item['raw_conf'] * 100:.2f}%"
                del item["raw_conf"]
            
            # Chuyển đổi ảnh đã vẽ khung màu thành chuỗi bytes định dạng .jpg
            _, img_encoded = cv2.imencode('.jpg', frame_to_save)
            img_bytes = img_encoded.tobytes()

            # Đóng gói Multipart gửi sang Backend
            files = {
                'image': ('detected_waste.jpg', img_bytes, 'image/jpeg')
            }
            payload = {
                'label': all_labels,
                'confidence': all_confs
            }
            
            try:
                requests.post(BACKEND_URL, data=payload, files=files, timeout=4)
            except Exception as e:
                print(f"[CẢNH BÁO KẾT NỐI] Không gửi ảnh và dữ liệu sang Backend lưu được: {e}")

            # 4. Trả kết quả về cho Giao diện hiển thị trực tiếp
            return jsonify({
                "status": "success", 
                "items": detected_items, 
                "label": all_labels,     # VD: "Rác tái chế, Rác độc hại"
                "confidence": all_confs, # VD: "95.00%, 85.00%"
                "box": detected_items[0]["box"] 
            }), 200
        else:
            return jsonify({"status": "success", "label": "Không nhận diện được"}), 200

    except Exception as e:
        print(f"[LỖI HỆ THỐNG CRASH]: {str(e)}")
        return jsonify({"status": "error", "message": f"Lỗi xử lý nội bộ AI: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
