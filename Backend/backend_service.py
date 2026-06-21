# Backend/backend_service.py
import datetime
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Cấu hình Cơ sở dữ liệu SQLite tại thư mục Backend
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'history_database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Thư mục chứa ảnh chụp từ camera nằm ngay tại Backend
UPLOAD_FOLDER = os.path.join(BASE_DIR, "saved_images")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# Cấu trúc bảng lưu trữ lịch sử phân loại
class WasteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    confidence = db.Column(db.String, nullable=False)
    image_path = db.Column(db.String, nullable=True) # Cột lưu đường dẫn file ảnh

# Tạo cơ sở dữ liệu nếu chưa có
with app.app_context():
    db.create_all()

@app.route('/save-result', methods=['POST'])
def save_result():
    """API nhận kết quả phân loại kèm FILE ẢNH thực tế để lưu vào thư mục và ghi đường dẫn vào DB"""
    # Lấy dữ liệu chữ từ request.form thay vì get_json do có đính kèm file
    label = request.form.get('label')
    confidence = request.form.get('confidence')
    
    if not label or not confidence:
        return jsonify({"status": "error", "message": "Thiếu thông tin dữ liệu label hoặc confidence."}), 400

    # Kiểm tra xem có file ảnh gửi kèm với key tên là 'image' không
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy dữ liệu file ảnh ('image') gửi tới Backend!"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "error", "message": "File ảnh gửi sang trống hoặc không hợp lệ."}), 400

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Tạo tên file ảnh ngẫu nhiên dựa vào timestamp để không trùng lặp
    filename = f"waste_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Chuỗi địa chỉ tương đối lưu vào Database (ví dụ: saved_images/waste_2026.jpg)
    relative_db_path = f"saved_images/{filename}"
    
    try:
        # 2. Thực hiện lưu file ảnh vật lý vào thư mục 'saved_images'
        file.save(file_path)
        
        # 3. Ghi thông tin và đường dẫn ảnh vào Database
        new_record = WasteHistory(
            timestamp=now,
            label=label,
            confidence=str(confidence),
            image_path=relative_db_path
        )
        
        db.session.add(new_record)
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "Đã lưu ảnh vật lý vào thư mục và ghi địa chỉ vào DB thành công!", 
            "id": new_record.id,
            "image_path": relative_db_path
        }), 200
    except Exception as e:
        db.session.rollback()
        # Nếu lưu database lỗi, chủ động xóa file ảnh vừa tạo để tránh rác thư mục
        if os.path.exists(file_path):
            os.remove(file_path)
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
        
        # Xóa file vật lý tương ứng nếu có đường dẫn
        if record.image_path:
            # Chuyển đổi ngược relative path thành absolute path để xóa file
            filename = record.image_path.split('/')[-1]
            target_file = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(target_file):
                os.remove(target_file)

        db.session.delete(record)
        db.session.commit()
        return jsonify({"status": "success", "message": "Xóa bản ghi và ảnh thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update-record/<int:record_id>', methods=['PUT'])
def update_record(record_id):

    record = WasteHistory.query.get(record_id)

    if not record:
        return jsonify({
            "status": "error",
            "message": "Không tìm thấy bản ghi"
        }), 404

    data = request.json

    record.label = data.get("label", record.label)
    record.confidence = data.get("confidence", record.confidence)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Cập nhật thành công"
    })

if __name__ == '__main__':
    print("Khởi động Backend Service tại http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)