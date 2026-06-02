# main.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import threading # THƯ VIỆN QUAN TRỌNG ĐỂ CHỐNG ĐƠ UI

from image_processor import resize_image, convert_frame_to_bytes
from api_client import upload_waste_image
from camera_handler import capture_from_webcam
from optionCamera import CameraOptionPopup

def quy_trinh_xu_ly_va_gui_anh(frame):
    """Quy trình khép kín: Tiền xử lý -> Đóng gói -> Gửi API"""
    try:
        anh_sach = resize_image(frame)
        du_lieu_bytes = convert_frame_to_bytes(anh_sach)
        
        print("Đang gửi ảnh sang hệ thống AI để dự đoán...")
        ket_qua = upload_waste_image(du_lieu_bytes)
        
        messagebox.showinfo("Kết quả phân loại", f"Hệ thống trả về:\n{ket_qua}")
        
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

def hanh_dong_tai_anh_tu_file():
    """Chạy ngầm luồng xử lý để không làm treo giao diện"""
    duong_dan_anh = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    
    if duong_dan_anh:
        frame = cv2.imread(duong_dan_anh, cv2.IMREAD_COLOR)
        if frame is None:
            messagebox.showwarning("Cảnh báo", "Không thể đọc ảnh. Vui lòng thử lại.")
            return
        # Bọc hàm gửi ảnh vào 1 thread riêng biệt
        threading.Thread(target=quy_trinh_xu_ly_va_gui_anh, args=(frame,), daemon=True).start()

def khoi_dong_camera_voi_id(camera_id):
    """Bật luồng Camera chạy song song với UI và truyền ID đã chọn vào"""
    print(f"Khởi động luồng Camera với ID: {camera_id}")
    
    # LƯU Ý: Nếu trong file camera_handler.py của bạn, hàm capture_from_webcam 
    # chưa nhận tham số camera_id, hãy đảm bảo sửa hàm đó thành: capture_from_webcam(on_capture_callback, camera_id)
    threading.Thread(
        target=capture_from_webcam, 
        args=(quy_trinh_xu_ly_va_gui_anh, camera_id), 
        daemon=True
    ).start()

def main():
    root = tk.Tk()
    root.title("Hệ Thống Phân Loại Rác Thải")
    root.geometry("400x250") 
    root.eval('tk::PlaceWindow . center')
    
    label_title = tk.Label(root, text="CHỌN PHƯƠNG THỨC LẤY ẢNH", font=("Arial", 14, "bold"))
    label_title.pack(pady=20)
    
    btn_upload = tk.Button(root, text="Tải ảnh từ máy tính", command=hanh_dong_tai_anh_tu_file, width=25, height=2, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
    btn_upload.pack(pady=10)
    
    # 2. SỬA LỆNH NÚT BẤM: Khởi tạo thực thể của Class khi click chuột
    btn_camera = tk.Button(
        root, 
        text="Sử dụng Camera trực tiếp", 
        command=lambda: CameraOptionPopup(root, khoi_dong_camera_voi_id), # Gọi Class tại đây
        width=25, height=2, bg="#2196F3", fg="white", font=("Arial", 10, "bold")
    )
    btn_camera.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()