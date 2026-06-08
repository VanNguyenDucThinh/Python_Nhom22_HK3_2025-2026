import os
import io
import sys
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
from ultralytics import YOLO

app = Flask(__name__)
<<<<<<< HEAD
CORS(app)  # Cho phep cac dịch vu khac port goi den nhau vinh vien

# =========================================================================
# FIX LỖI 1: Chuyển port từ 8000 sang 5000 để AI Service gọi đúng vào Backend
# =========================================================================
BACKEND_URL = "http://127.0.0.1:5000/save-result"

# Xác định đường dẫn mô hình YOLOv8
AI_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(AI_SERVICE_DIR)
MODEL_PATH = os.path.join(PROJECT_ROOT, "runs", "detect", "train", "weights", "best.pt")

print(f"[AI SERVICE] Dang tai mo hinh tu: {MODEL_PATH}")
=======
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
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a

try:
    model = YOLO(MODEL_PATH)
    print("[AI SERVICE] Tai mo hinh YOLOv8 thanh cong!")
except Exception as e:
    print(f"[AI SERVICE LỖI NẶNG]: Khong the tai mo hinh. Chi tiet: {e}")
    sys.exit(1)

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "Khong tim thay file anh trong yeu cau"}), 400

    try:
<<<<<<< HEAD
        # Doc anh tu request gửi len
=======
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
        file = request.files['image']
        in_memory_file = io.BytesIO()
        file.save(in_memory_file)
        data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"status": "error", "message": "File anh bi loi hoac khong hop le"}), 400

<<<<<<< HEAD
        # Dua vao YOLOv8 de du doan phan loai rac
        results = model(image)
        
        raw_label = "Khong xac dinh"
        confidence = 0.0
=======
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
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a

        for result in results:
            boxes = result.boxes
            if len(boxes) > 0:
                # Lay doi tuong co do tin cay cao nhat trong anh
                best_box_idx = np.argmax(boxes.conf.cpu().numpy())
                class_id = int(boxes.cls[best_box_idx])
                raw_label = model.names[class_id]
                confidence = float(boxes.conf[best_box_idx])
                break

<<<<<<< HEAD
        # =========================================================================
        # FIX LỖI ĐỒNG BỘ: Dịch nhãn chuẩn theo bộ đếm tiếng Việt và có "Không nhận diện được"
        # =========================================================================
        raw_label = raw_label.lower().strip()
        
        if "organic" in raw_label or "huu_co" in raw_label or "bio" in raw_label:
=======
        if "inorganic" in raw_label or "vo_co" in raw_label:
            label = "Rác vô cơ"
        elif "organic" in raw_label or "huu_co" in raw_label:
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
            label = "Rác hữu cơ"
        elif "recycle" in raw_label or "tai_che" in raw_label:
            label = "Rác tái chế"
        elif "hazard" in raw_label or "doc_hai" in raw_label:
            label = "Rác độc hại"
        elif "inorganic" in raw_label or "vo_co" in raw_label:
            label = "Rác vô cơ"
        else:
            label = "Không nhận diện được"

<<<<<<< HEAD
        conf_str = f"{confidence * 100:.2f}%"
        print(f"[AI SERVICE] Ket qua: {label} ({conf_str})")

        # =========================================================================
        # FIX LỖI 2: Đổi tham số từ data= thành json= để Flask Backend doc duoc du lieu
        # =========================================================================
=======
        print(f"[AI SERVICE] Object Detection -> Nhãn gốc: '{raw_label}' | Nhãn dịch: '{label}' | Tọa độ khung: {box_coords}")

        # 4. Gửi kết quả sang Backend để lưu Database
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
        result_data = {
            "label": label,
            "confidence": conf_str
        }
        
        try:
<<<<<<< HEAD
            # Tu dong ban du lieu sang Backend ngay lap tuc de ghi file .db
            response_db = requests.post(BACKEND_URL, json=result_data, timeout=3)
            print(f"[AI SERVICE -> BACKEND]: Trang thai luu DB: {response_db.status_code}")
        except Exception as err_db:
            print(f"[CANH BAO]: Khong the ket noi Port 5000 de luu DB. Chi tiet: {err_db}")

        # Tra ket qua nguoc lai cho Giao dien hien thi chu mau xanh
        return jsonify({
            "status": "success",
            "label": label,
            "confidence": conf_str
        }), 200

    except Exception as e:
        print(f"[AI SERVICE LỖI HE THONG]: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8000, debug=True)
=======
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
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
