# camera_handler.py
import cv2
from config import CAMERA_INDEX

def capture_from_webcam(on_capture_callback):
    """Mở luồng camera, hiển thị giao diện và đợi nhấn 'S' để chụp ảnh"""
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print("Lỗi: Không thể mở Camera thiết bị.")
        return

    print("Đang mở Camera... Nhấn 'S' để chụp hình rác thải, 'Q' để thoát.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Lỗi: Không thể đọc dữ liệu từ Camera.")
                break

            cv2.imshow("Camera Service - Luong truc tiep", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):  # Nhấn 'S' để chụp
                print("Đang chụp và xử lý khung hình...")
                try:
                    on_capture_callback(frame)
                except Exception as exc:
                    print(f"Lỗi khi xử lý khung hình: {exc}")
                break
            elif key == ord('q'):  # Nhấn 'Q' để tắt camera
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()