# api_client.py
import requests
from config import API_URL

def upload_waste_image(image_bytes):
    """Đóng gói và gửi dữ liệu ảnh nhị phân qua REST API"""
    # Đóng gói file theo chuẩn multipart/form-data
    files = {'image': ('waste.jpg', image_bytes, 'image/jpeg')}
    
    try:
        response = requests.post(API_URL, files=files, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"status": "error", "message": f"Lỗi kết nối API: {exc}"}
    except ValueError:
        return {"status": "error", "message": "API trả về dữ liệu không hợp lệ."}