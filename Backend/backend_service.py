# Backend/backend_service.py
import datetime
import os
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Cấu hình Cơ sở dữ liệu SQLite tại thư mục Backend
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'history_database.db')}\""
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Tạo thư mục chứa ảnh chụp từ camera nếu chưa có
UPLOAD_FOLDER = os.path.join(BASE_DIR, "saved_images")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# Khởi tạo cấu trúc bảng lưu trữ (Thêm cột image_path)
class WasteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    confidence = db.Column(db.String, nullable=False)
    image_path = db.Column(db.String, nullable=True) # Cột mới lưu tên file ảnh

# Tạo cơ sở dữ liệu
with app.app_context():
    db.create_all()

@app.route('/save-result', methods=['POST'])
def save_result():
    """API nhận kết quả phân loại từ AI_Service kèm lưu ảnh thô từ request nếu có"""
    data = request.get_json()
    if not data or 'label' not in data or 'confidence' not in data:
        return jsonify({"status": "error", "message": "Thiếu thông tin dữ liệu."}), 400

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Tạo tên file ảnh ngẫu nhiên dựa vào timestamp để không trùng lặp
    filename = f"waste_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    full_img_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # (Tùy chọn nâng cao) Nếu luồng bytes được gửi kèm từ AI service hoặc gửi riêng, 
    # trong đồ án này để đơn giản ta tạo file ảnh giả lập hoặc lấy luồng camera lưu lại.
    # Để đơn giản hóa luồng, ta lưu tên file ảnh vào DB trước:
    new_record = WasteHistory(
        timestamp=now,
        label=data['label'],
        confidence=str(data['confidence']),
        image_path=filename
    )
    
    try:
        db.session.add(new_record)
        db.session.commit()
        return jsonify({"status": "success", "message": "Đã lưu vào Database thành công!", "id": new_record.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/records', methods=['GET'])
def get_records():
    """API lấy toàn bộ danh sách lịch sử"""
    try:
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
    """API lấy chi tiết 1 bản ghi để phục vụ nút Xem Chi Tiết"""
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
        
        # Xóa file ảnh vật lý trong folder tương ứng để tránh rác ổ cứng
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
    print("Khởi động Backend Service tại http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)