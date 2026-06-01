# camera_handler.py
import cv2
from ultralytics import YOLO
from config import CAMERA_INDEX

def capture_from_webcam(on_capture_callback):
    """
    Sử dụng AI YOLOv8 để CHỈ tự động phát hiện RÁC THẢI (Chai, ly, cốc, bát...).
    Bỏ qua con người và toàn bộ các vật thể di chuyển khác không phải rác.
    """
    # Tải mô hình YOLOv8 siêu nhẹ
    model = YOLO("yolov8n.pt")
    
    # LỌC CHỈ LẤY RÁC: 
    # 39: bottle (chai nhựa/thủy tinh), 41: cup (ly, cốc nhựa/giấy), 45: bowl (bát mì, hộp xốp)
    RAC_WASTE_CLASSES = [39, 41, 45] 

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Lỗi: Không thể mở Camera thiết bị.")
        return

    print("Hệ thống quét RÁC THẢI tự động đã bật... Nhấn 'S' để chụp vùng rác, 'Q' để thoát.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Lỗi: Không thể đọc dữ liệu từ Camera.")
                break

            display = frame.copy()
            
            # Đưa hình ảnh vào cho AI phân tích (tắt log in ra terminal để chạy mượt hơn)
            results = model(frame, verbose=False)
            
            co_rac_trong_khung = False
            toa_do_cuc_bo = None

            # Duyệt qua tất cả các mục AI tìm thấy
            for box in results[0].boxes:
                class_id = int(box.cls[0])      # Lấy mã ID của vật thể
                conf = float(box.conf[0])       # Độ tự tin của AI (từ 0 đến 1)
                
                # CHỈ xử lý nếu vật thể tìm thấy nằm trong danh mục RÁC và độ chính xác > 50%
                if class_id in RAC_WASTE_CLASSES and conf > 0.5:
                    # Lấy tọa độ hộp khung của rác
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Đổi tên hiển thị sang tiếng Việt cho thân thiện
                    ten_tieng_anh = model.names[class_id]
                    ten_tieng_viet = "Chai/Lo" if ten_tieng_anh == "bottle" else "Ly/Coc" if ten_tieng_anh == "cup" else "Hop/Bat xop"
                    
                    # Vẽ KHUNG MÀU ĐỎ bám sát theo viên rác thải
                    cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(display, f"{ten_tieng_viet} ({conf*100:.1f}%)", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    
                    # Ghi nhận tọa độ để chuẩn bị cắt ảnh
                    toa_do_cuc_bo = (x1, y1, x2, y2)
                    co_rac_trong_khung = True
                    break # Ưu tiên xử lý rác thải rõ nhất trước

            # Hiển thị giao diện quét rác trực tiếp
            cv2.imshow("AI Waste Scanner - Thong minh", display)
            
            key = cv2.waitKey(1) & 0xFF
            
            # Nếu có rác trong tầm ngắm và bấm phím 'S'
            if key == ord('s') or key == ord('S'):
                if co_rac_trong_khung and toa_do_cuc_bo:
                    x1, y1, x2, y2 = toa_do_cuc_bo
                    
                    # Cắt gọn bức ảnh chỉ lấy phần rác thải, loại bỏ toàn bộ nền phòng/con người xung quanh
                    cropped_frame = frame[y1:y2, x1:x2]
                    print("Đã chụp và cắt ảnh rác thải thành công!")
                    
                    # Gửi ảnh cắt sang hệ thống phân loại của main.py
                    on_capture_callback(cropped_frame)
                    break
                else:
                    print("Không tìm thấy rác thải hợp lệ trong khung hình để chụp phân loại!")
                    
            elif key == ord('q') or key == ord('Q'):
                print("Đã đóng luồng camera.")
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()