# Backend/backend_service.py
import datetime
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# FIX lỗi dấu nháy kép thừa: Cấu hình Cơ sở dữ liệu SQLite sạch
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'history_database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Tạo thư mục chứa ảnh chụp nếu chưa có
UPLOAD_FOLDER = os.path.join(BASE_DIR, "saved_images")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# Khởi tạo cấu trúc bảng lưu trữ
class WasteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    confidence = db.Column(db.String, nullable=False)
    image_path = db.Column(db.String, nullable=True)

# Khởi tạo database và bảng dữ liệu ban đầu
with app.app_context():
    db.create_all()

@app.route('/save-result', methods=['POST'])
def save_result():
    try:
        data = request.get_json()
        if not data or 'label' not in data or 'confidence' not in data:
            return jsonify({"status": "error", "message": "Dữ liệu gửi lên thiếu thông tin"}), 400

        # Tự động đồng bộ mốc thời gian thực của hệ thống máy tính
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Tự động sinh tên file ảnh ngẫu nhiên theo mốc thời gian để UI lấy làm căn cứ ghi file vật lý
        time_slug = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        generated_img_name = f"waste_{time_slug}.jpg"

        new_record = WasteHistory(
            timestamp=now_str,
            label=data['label'],
            confidence=data['confidence'],
            image_path=generated_img_name
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        print(f"[BACKEND] Đã lưu thành công bản ghi #{new_record.id} vào Database.")
        return jsonify({"status": "success", "message": "Đã lưu lịch sử thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# BỔ SUNG ENDPOINT lấy toàn bộ danh sách (để phục vụ giao diện hiển thị bảng Treeview)
@app.route('/api/records', methods=['GET'])
def get_all_records():
    try:
        # Lấy toàn bộ danh sách, xếp mã ID mới nhất lên đầu bảng
        records = WasteHistory.query.order_by(WasteHistory.id.desc()).all()
        result = []
        for r in records:
            result.append({
                "id": r.id,
                "timestamp": r.timestamp,
                "label": r.label,
                "confidence": r.confidence,
                "image_path": r.image_path
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/record/<int:record_id>', methods=['GET'])
def get_record_detail(record_id):
    record = WasteHistory.query.get(record_id)
    if not record:
        return jsonify({"status": "error", "message": "Không tìm thấy bản ghi"}), 404
    return jsonify({
        "id": record.id,
        "timestamp": record.timestamp,
        "label": record.label,
        "confidence": record.confidence,
        "image_path": record.image_path
    }), 200

@app.route('/delete-record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    try:
        record = WasteHistory.query.get(record_id)
        if not record:
            return jsonify({"status": "error", "message": "Không tìm thấy bản ghi này!"}), 404
        
        if record.image_path:
            target_file = os.path.join(UPLOAD_FOLDER, record.image_path)
            if os.path.exists(target_file):
                os.remove(target_file)

        db.session.delete(record)
        db.session.commit()
        return jsonify({"status": "success", "message": "Xóa thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)