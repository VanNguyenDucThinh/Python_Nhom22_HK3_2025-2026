# camera_handler.py
import cv2
from ultralytics import YOLO
from config import CAMERA_INDEX

def capture_from_webcam(on_capture_callback, camera_id_chosen):
    """
    Camera Service: Chỉ quét vị trí vật thể tiềm năng, vẽ khung vuông đỏ định vị 
    và cắt ảnh gửi đi khi nhấn phím 'S'. Không đảm nhận nhiệm vụ phân loại sâu.
    """
    # Tải mô hình YOLOv8 siêu nhẹ để lấy bounding box nhanh
    model = YOLO("yolov8n.pt")
    
    # Danh sách các ID vật thể tiềm năng cần theo vết (Chai, ly, cốc, bát, đĩa, thức ăn...)
    TARGET_CLASSES = [34, 39, 41, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 66]

    cap = cv2.VideoCapture(camera_id_chosen)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    if not cap.isOpened():
        print("Lỗi: Không thể mở Camera thiết bị.")
        return

    print("Camera Service đang chạy... Nhấn 'S' để chụp vùng chọn, 'Q' để thoát.")
    
    # Bộ đệm ổn định khung hình (Memory Buffer) chống chớp nháy khung khi cử động
    toa_do_on_dinh = None
    khung_cho_phep_mat = 12  # Giữ khung hình cũ trong ~0.4 giây nếu mất dấu tạm thời
    dem_khung_mat_dau = 0     

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Lỗi: Không thể đọc dữ liệu từ Camera.")
                break

            display = frame.copy()
            
            # Sử dụng tracking giúp bám dính vật thể khi di chuyển camera
            results = model.track(frame, persist=True, verbose=False)
            
            co_vat_the_trong_khung = False

            if results[0].boxes and results[0].boxes.id is not None:
                for box in results[0].boxes:
                    class_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Lọc theo danh sách ID mục tiêu và độ tin cậy > 40%
                    if class_id in TARGET_CLASSES and conf > 0.4:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        toa_do_on_dinh = (x1, y1, x2, y2)
                        co_vat_the_trong_khung = True
                        dem_khung_mat_dau = 0 
                        break # Khóa mục tiêu rõ nhất trong khung hình

            # Logic giữ khung thông minh từ bộ đệm nếu bị khuất hoặc nhòe hình
            if not co_vat_the_trong_khung and toa_do_on_dinh is not None:
                dem_khung_mat_dau += 1
                if dem_khung_mat_dau > khung_cho_phep_mat:
                    toa_do_on_dinh = None

            # CHỈ VẼ MỖI HÌNH VUÔNG ĐỎ ĐỂ XÁC ĐỊNH VẬT THỂ
            if toa_do_on_dinh is not None:
                rx1, ry1, rx2, ry2 = toa_do_on_dinh
                # Giới hạn tọa độ để không bị tràn ra ngoài biên ảnh
                rx1, ry1 = max(0, rx1), max(0, ry1)
                rx2, ry2 = min(frame.shape[1], rx2), min(frame.shape[0], ry2)

                # Vẽ duy nhất khung vuông màu đỏ, dày 2px, không kèm text
                cv2.rectangle(display, (rx1, ry1), (rx2, ry2), (0, 0, 255), 2)

            cv2.imshow("Camera Service - Object Tracker", display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s') or key == ord('S'):
                if toa_do_on_dinh is not None:
                    rx1, ry1, rx2, ry2 = toa_do_on_dinh
                    cropped_frame = frame[ry1:ry2, rx1:rx2]
                    
                    if cropped_frame.size > 0:
                        print("Đã chụp và cắt vùng ảnh vật thể thành công. Gửi đến bộ phân loại...")
                        on_capture_callback(cropped_frame)
                        break
                else:
                    print("Không có mục tiêu nào trong khung vuông để chụp!")
                    
            elif key == ord('q') or key == ord('Q'):
                print("Đã đóng luồng camera.")
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()