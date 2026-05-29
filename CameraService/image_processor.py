# image_processor.py
import cv2
from config import TARGET_IMAGE_SIZE

def resize_image(frame):
    """Thay đổi kích thước khung hình về chuẩn AI yêu cầu"""
    if frame is None:
        raise ValueError("Frame ảnh không hợp lệ.")
    return cv2.resize(frame, TARGET_IMAGE_SIZE)

def convert_frame_to_bytes(frame):
    """Mã hóa ma trận ảnh OpenCV thành dữ liệu nhị phân (bytes) để gửi qua API"""
    if frame is None:
        raise ValueError("Frame ảnh không hợp lệ.")

    # Mã hóa ảnh sang định dạng .jpg trong bộ nhớ tạm
    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        raise ValueError("Không thể mã hóa hình ảnh.")
    
    # Chuyển đổi thành chuỗi bytes nhị phân
    return encoded_image.tobytes()