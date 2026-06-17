# Backend/backend_service.py
import datetime
import os
<<<<<<< HEAD
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
=======
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Đảm bảo hiển thị tiếng Việt chuẩn không lỗi font
>>>>>>> main

# Cấu hình Cơ sở dữ liệu SQLite tại thư mục Backend
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'history_database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Thư mục chứa ảnh chụp từ camera nằm ngay tại Backend
UPLOAD_FOLDER = os.path.join(BASE_DIR, "saved_images")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

<<<<<<< HEAD
# Cấu trúc bảng lưu trữ lịch sử phân loại
=======
# ==============================================================================
# 1. CẬP NHẬT CẤU TRÚC BẢNG: THÊM CỘT THỨ 5 (image_name)
# ==============================================================================
>>>>>>> main
class WasteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    confidence = db.Column(db.String, nullable=False)
<<<<<<< HEAD
    image_path = db.Column(db.String, nullable=True) # Cột lưu đường dẫn file ảnh

# Tạo cơ sở dữ liệu nếu chưa có
=======
    image_name = db.Column(db.String, nullable=True)  # Cột thứ 5 lưu tên file ảnh liên kết

# Tạo cơ sở dữ liệu nếu chưa tồn tại
>>>>>>> main
with app.app_context():
    db.create_all()

# Tạo thư mục chứa ảnh nếu chưa có
SAVED_IMAGES_DIR = os.path.join(BASE_DIR, 'saved_images')
if not os.path.exists(SAVED_IMAGES_DIR):
    os.makedirs(SAVED_IMAGES_DIR)

# ==============================================================================
# 2. ROUTE SERVE HÌNH ẢNH VẬT LÝ TỪ THƯ MỤC Backend/saved_images
# ==============================================================================
@app.route('/saved_images/<filename>', methods=['GET'])
def serve_image(filename):
    """Hỗ trợ tải và hiển thị ảnh trực tiếp từ folder thông qua URL"""
    return send_from_directory(SAVED_IMAGES_DIR, filename)

# ==============================================================================
# 3. CẬP NHẬT API NHẬN KẾT QUẢ ĐỂ LƯU THÊM TÊN ẢNH KHÓA NGOẠI
# ==============================================================================
@app.route('/save-result', methods=['POST'])
def save_result():
<<<<<<< HEAD
    """API nhận kết quả phân loại kèm FILE ẢNH thực tế để lưu vào thư mục và ghi đường dẫn vào DB"""
    # Lấy dữ liệu chữ từ request.form thay vì get_json do có đính kèm file
    label = request.form.get('label')
    confidence = request.form.get('confidence')
=======
    """API nhận kết quả phân loại từ AI_Service / CameraView"""
    data = request.get_json()
>>>>>>> main
    
    if not label or not confidence:
        return jsonify({"status": "error", "message": "Thiếu thông tin dữ liệu label hoặc confidence."}), 400

<<<<<<< HEAD
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
=======
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Lấy tên ảnh từ client truyền sang (nếu không có thì mặc định None)
    img_name = data.get('image_name', None)

    try:
        new_record = WasteHistory(
            timestamp=now,
            label=data['label'],
            confidence=data['confidence'],
            image_name=img_name
>>>>>>> main
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({
            "status": "success", 
<<<<<<< HEAD
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
=======
            "message": "Đã lưu lịch sử và liên kết ảnh thành công.",
            "id": new_record.id
        }), 200
>>>>>>> main
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

<<<<<<< HEAD
=======
# ==============================================================================
# 4. CẬP NHẬT VIEW HTML ĐỂ HIỂN THỊ CỘT THỨ 5 TRÊN TRÌNH DUYỆT WEB
# ==============================================================================
@app.route('/', methods=['GET'])
def index():
    """Xem danh sách lịch sử dạng Dashboard rút gọn trên Web"""
    records = WasteHistory.query.order_by(WasteHistory.id.desc()).all()
    
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Hệ thống Quản lý Lịch sử Phân loại Rác</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 30px; background-color: #f4f6f9; }
            h2 { color: #2c3e50; text-align: center; margin-bottom: 25px; }
            .container { max-width: 950px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #00b050; color: white; }
            tr:hover { background-color: #f8f9fa; }
            .badge { padding: 5px 10px; border-radius: 20px; color: white; font-size: 12px; font-weight: bold; }
            .huu-co { background-color: #2ecc71; }
            .vo-co { background-color: #e67e22; }
            .tai-che { background-color: #3498db; }
            .doc-hai { background-color: #e74c3c; }
            .img-link { color: #00b050; text-decoration: none; font-weight: 500; }
            .img-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📊 LỊCH SỬ PHÂN LOẠI RÁC THẢI (DỮ LIỆU ĐỒ ÁN NHÓM)</h2>
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Thời Gian Quét</th>
                        <th>Loại Rác Phát Hiện</th>
                        <th>Độ Tin Cậy</th>
                        <th>Hình Ảnh Lưu Trữ</th> </tr>
                </thead>
                <tbody>
                    {% for row in records %}
                    <tr>
                        <td>#{{ row.id }}</td>
                        <td>{{ row.timestamp }}</td>
                        <td>
                            {% if row.label == "Rác hữu cơ" %}
                                <span class="badge huu-co">{{ row.label }}</span>
                            {% elif row.label == "Rác vô cơ" %}
                                <span class="badge vo-co">{{ row.label }}</span>
                            {% elif row.label == "Rác tái chế" %}\
                                <span class="badge tai-che">{{ row.label }}</span>
                            {% elif row.label == "Rác độc hại" %}
                                <span class="badge doc-hai">{{ row.label }}</span>
                            {% else %}
                                <span class="badge" style="background-color: #7f8c8d;">{{ row.label }}</span>
                            {% endif %}
                        </td>
                        <td><strong style="color: #2c3e50;">{{ row.confidence }}</strong></td>
                        <td>
                            {% if row.image_name %}
                                <a class="img-link" href="/saved_images/{{ row.image_name }}" target="_blank">🖼️ {{ row.image_name }}</a>
                            {% else %}
                                <span style="color: #bdc3c7; font-style: italic;">Không có ảnh</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, records=records)

>>>>>>> main
if __name__ == '__main__':
    print("Khởi động Backend Service tại http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)