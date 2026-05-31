# Backend/backend_service.py
import datetime
import os
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cấu hình lưu trữ Cơ sở dữ liệu SQLite ngay tại thư mục Backend
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'history_database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Định nghĩa bảng dữ liệu lưu trữ lịch sử phân loại rác
class WasteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    confidence = db.Column(db.String, nullable=False)

# Tạo file Database và bảng nếu chưa tồn tại
with app.app_context():
    db.create_all()

@app.route('/save-result', methods=['POST'])
def save_result():
    """API tiếp nhận kết quả từ AI Service truyền sang để lưu vào DB"""
    data = request.get_json()
    
    if not data or 'label' not in data or 'confidence' not in data:
        return jsonify({"status": "error", "message": "Dữ liệu gửi tới thiếu thông tin."}), 400

    try:
        # Lấy mốc thời gian hiện tại
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Tạo bản ghi mới
        new_record = WasteHistory(
            timestamp=current_time,
            label=data['label'],
            confidence=f"{float(data['confidence']) * 100:.2f}%"
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        print(f"[BACKEND] Đã lưu vào DB: {data['label']} lúc {current_time}")
        return jsonify({"status": "success", "message": "Đã lưu lịch sử vào Database thành công."}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[BACKEND LỖI] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/history', methods=['GET'])
def show_history():
    """Giao diện xem bảng lịch sử phân loại rác trực quan trên trình duyệt (Static Table)"""
    records = WasteHistory.query.order_by(WasteHistory.id.desc()).all()
    
    # Giao diện HTML tối giản tích hợp trực tiếp để bạn không cần tạo file .html riêng
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lịch Sử Phân Loại Rác Thải</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; }
            h2 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>BẢNG THỐNG KÊ LỊCH SỬ PHÂN LOẠI RÁC THẢI (STATIC TABLE)</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Thời Gian Ghi Nhận</th>
                <th>Loại Rác Phân Loại</th>
                <th>Độ Chính Xác (Confidence)</th>
            </tr>
            {% for row in records %}
            <tr>
                <td>{{ row.id }}</td>
                <td>{{ row.timestamp }}</td>
                <td><strong>{{ row.label }}</strong></td>
                <td>{{ row.confidence }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, records=records)

if __name__ == '__main__':
    print("Khởi động Backend Service tại http://127.0.0.1:5000")
    # Chạy ở cổng 5000 phục vụ lưu DB và xem giao diện lịch sử
    app.run(host='0.0.0.0', port=5000, debug=True)