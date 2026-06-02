import sys
sys.stdout.reconfigure(encoding='utf-8')
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import threading # THƯ VIỆN QUAN TRỌNG ĐỂ CHỐNG ĐƠ UI

from image_processor import resize_image, convert_frame_to_bytes
from api_client import upload_waste_image
from camera_handler import capture_from_webcam

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

def hanh_dong_su_dung_camera():
    """Bật luồng Camera chạy song song với UI"""
    threading.Thread(target=capture_from_webcam, args=(quy_trinh_xu_ly_va_gui_anh,), daemon=True).start()

def main():
    root = tk.Tk()
    root.title("Hệ Thống Phân Loại Rác Thải")
    
    # kích thước cửa sổ
    window_width = 600
    window_height = 450
    
    # Lấy thông số màn hình và tính toán căn giữa
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}') 
    
    # 2. Tăng font chữ tiêu đề và khoảng cách
    label_title = tk.Label(root, text="CHỌN PHƯƠNG THỨC LẤY ẢNH", font=("Arial", 16, "bold"))
    label_title.pack(pady=40) # Tăng khoảng cách phía trên
    
    # 3. Kéo dài nút bấm (width=30) và tăng cỡ chữ (11)
    btn_upload = tk.Button(root, text="Tải ảnh từ máy tính", command=hanh_dong_tai_anh_tu_file, 
                           width=30, height=2, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
    btn_upload.pack(pady=15)
    
    btn_camera = tk.Button(root, text="Sử dụng Camera trực tiếp", command=hanh_dong_su_dung_camera, 
                           width=30, height=2, bg="#2196F3", fg="white", font=("Arial", 11, "bold"))
    btn_camera.pack(pady=15)
    
    root.mainloop()
if __name__ == "__main__":
    main()