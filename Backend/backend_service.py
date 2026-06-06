# Backend/backend_service.py
import datetime
import os
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cấu hình Cơ sở dữ liệu SQLite tại thư mục Backend
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'history_database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Khởi tạo cấu trúc bảng lưu trữ
class WasteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    confidence = db.Column(db.String, nullable=False)

# Tạo cơ sở dữ liệu
with app.app_context():
    db.create_all()

@app.route('/save-result', methods=['POST'])
def save_result():
    """API nhận kết quả phân loại từ AI_Service"""
    data = request.get_json()
    
    if not data or 'label' not in data or 'confidence' not in data:
        return jsonify({"status": "error", "message": "Thiếu thông tin dữ liệu."}), 400

    try:
        current_time = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        
        # Tạo bản ghi cất vào Database
        new_record = WasteHistory(
            timestamp=current_time,
            label=data['label'],
            confidence=data['confidence'] # Nhận chuỗi phần trăm định dạng sẵn từ AI Service
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        print(f"[BACKEND] Đã lưu lịch sử: {data['label']} ({new_record.confidence})")
        return jsonify({"status": "success", "message": "Lưu Database thành công."}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/history', methods=['GET'])
def show_history():
    """Giao diện Bảng thống kê lịch sử (Static Table) hiển thị trên Trình duyệt"""
    records = WasteHistory.query.order_by(WasteHistory.id.desc()).all()
    
    # Giao diện HTML bổ sung màu sắc phân biệt cho 4 loại rác
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Kết Quả Thống Kê Phân Loại Rác</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f4f6f9; color: #333; }
            .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            h2 { text-align: center; color: #2c3e50; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 1px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 14px; text-align: center; border-bottom: 1px solid #e0e0e0; }
            th { background-color: #2c3e50; color: white; font-weight: 600; }
            tr:hover { background-color: #f8f9fa; }
            .badge { padding: 6px 12px; border-radius: 20px; color: white; font-weight: bold; font-size: 13px; display: inline-block; }
            .huu-co { background-color: #2ed573; }   /* Màu xanh lá cho hữu cơ */
            .vo-co { background-color: #ff4757; }     /* Màu đỏ cho vô cơ */
            .tai-che { background-color: #1e90ff; }   /* Màu xanh dương cho tái chế */
            .doc-hai { background-color: #9b59b6; }   /* Màu tím cho độc hại */
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Bảng Thống Kê Lịch Sử Phân Loại Rác Thải</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID Bản Ghi</th>
                        <th>Thời Gian Thu Nhận</th>
                        <th>Phân Loại Rác</th>
                        <th>Độ Tin Cậy (Confidence)</th>
                    </tr>
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
                            {% elif row.label == "Rác tái chế" %}
                                <span class="badge tai-che">{{ row.label }}</span>
                            {% elif row.label == "Rác độc hại" %}
                                <span class="badge doc-hai">{{ row.label }}</span>
                            {% else %}
                                <span class="badge" style="background-color: #7f8c8d;">{{ row.label }}</span>
                            {% endif %}
                        </td>
                        <td><strong style="color: #2c3e50;">{{ row.confidence }}</strong></td>
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