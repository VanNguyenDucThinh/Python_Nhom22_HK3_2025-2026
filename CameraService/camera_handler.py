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
    
    # Đặt tên cửa sổ thành một biến cố định để dễ quản lý
    WINDOW_NAME = "Camera Service - Luong truc tiep"
    
    # Tạo cửa sổ trước khi vào vòng lặp
    cv2.namedWindow(WINDOW_NAME)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Lỗi: Không thể đọc dữ liệu từ Camera.")
                break

            # 1. Vẽ cửa sổ
            cv2.imshow(WINDOW_NAME, frame)

            # 2. BẮT BUỘC ĐỂ WAITKEY Ở ĐÂY để OpenCV xử lý sự kiện click chuột
            key = cv2.waitKey(1) & 0xFF

            # 3. KIỂM TRA NÚT X (Sau khi waitKey đã chạy)
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                print("Đã tắt Camera.")
                break

            # 4. KIỂM TRA PHÍM BẤM S, Q
            if key == ord('s'):  # Nhấn 'S' để chụp
                print("Đang chụp và xử lý khung hình...")
                try:
                    on_capture_callback(frame)
                except Exception as exc:
                    print(f"Lỗi khi xử lý khung hình: {exc}")
                break
            elif key == ord('q'):  # Nhấn 'Q' để tắt camera
                print("Đã tắt Camera bằng phím Q.")
                break                
    finally:
        # Giải phóng camera và đóng tất cả cửa sổ an toàn
        cap.release()
        cv2.destroyAllWindows()