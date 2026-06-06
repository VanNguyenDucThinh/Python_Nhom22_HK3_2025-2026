# CameraService/image_processor.py
import cv2

def resize_image(frame):
    """
    [CẬP NHẬT CHO YOLOv8]: Không còn ép kích thước cố định làm bóp méo hình ảnh nữa.
    Trả về nguyên bản khung hình để YOLOv8 tự động xử lý đệm ảnh (Letterboxing) thông minh,
    giúp tối ưu hóa độ chính xác khi nhận diện vật thể.
    """
    if frame is None:
        raise ValueError("Khung hình ảnh không hợp lệ (None).")
    
    # Trả về chính nó mà không thay đổi kích thước (Chống méo hình)
    return frame

def convert_frame_to_bytes(frame):
    """
    Mã hóa ma trận ảnh OpenCV thành dữ liệu nhị phân (bytes) chất lượng cao 
    để đóng gói gửi qua REST API (Multipart/Form-Data).
    """
    if frame is None:
        raise ValueError("Khung hình ảnh không hợp lệ để mã hóa.")

    # Mã hóa ảnh sang định dạng đuôi mở rộng .jpg trong bộ nhớ tạm
    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        raise ValueError("Hệ thống không thể mã hóa hình ảnh sang định dạng JPEG.")
    
    # Chuyển đổi mảng ma trận tạm thành chuỗi bytes nhị phân thuần túy
    return encoded_image.tobytes()