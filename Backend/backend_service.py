# Backend/backend_service.py
import datetime
import os
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Đảm bảo hiển thị tiếng Việt chuẩn không lỗi font

# Cấu hình Cơ sở dữ liệu SQLite tại thư mục Backend
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'history_database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==============================================================================
# 1. CẬP NHẬT CẤU TRÚC BẢNG: THÊM CỘT THỨ 5 (image_name)
# ==============================================================================
class WasteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    confidence = db.Column(db.String, nullable=False)
    image_name = db.Column(db.String, nullable=True)  # Cột thứ 5 lưu tên file ảnh liên kết

# Tạo cơ sở dữ liệu nếu chưa tồn tại
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
    """API nhận kết quả phân loại từ AI_Service / CameraView"""
    data = request.get_json()
    
    if not data or 'label' not in data or 'confidence' not in data:
        return jsonify({"status": "error", "message": "Thiếu thông tin dữ liệu."}), 400

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Lấy tên ảnh từ client truyền sang (nếu không có thì mặc định None)
    img_name = data.get('image_name', None)

    try:
        new_record = WasteHistory(
            timestamp=now,
            label=data['label'],
            confidence=data['confidence'],
            image_name=img_name
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({
            "status": "success", 
            "message": "Đã lưu lịch sử và liên kết ảnh thành công.",
            "id": new_record.id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

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

if __name__ == '__main__':
    print("Khởi động Backend Service thành công tại http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)