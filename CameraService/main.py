# main.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from image_processor import resize_image, convert_frame_to_bytes
from api_client import upload_waste_image
from camera_handler import capture_from_webcam

def quy_trinh_xu_ly_va_gui_anh(frame):
    """Quy trình khép kín: Tiền xử lý -> Đóng gói -> Gửi API"""
    try:
        anh_sach = resize_image(frame)
        du_lieu_bytes = convert_frame_to_bytes(anh_sach)
        
        print("Đang gửi ảnh sang hệ thống...")
        ket_qua = upload_waste_image(du_lieu_bytes)
        
        # Hiển thị thông báo dạng Pop-up cho người dùng biết kết quả
        messagebox.showinfo("Kết quả phân loại", f"Hệ thống trả về:\n{ket_qua}")
        
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

def hanh_dong_tai_anh_tu_file():
    """Logic cho Nút bấm 1: Chọn ảnh từ thiết bị"""
    duong_dan_anh = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    
    if duong_dan_anh:
        frame = cv2.imread(duong_dan_anh, cv2.IMREAD_COLOR)
        if frame is None:
            messagebox.showwarning("Cảnh báo", "Không thể đọc ảnh. Vui lòng thử lại.")
            return
        quy_trinh_xu_ly_va_gui_anh(frame)

def hanh_dong_su_dung_camera():
    """Logic cho Nút bấm 2: Sử dụng webcam"""
    capture_from_webcam(quy_trinh_xu_ly_va_gui_anh)

def main():
    """Xây dựng giao diện người dùng (GUI) với Tkinter"""
    # Khởi tạo cửa sổ chính
    root = tk.Tk()
    root.title("Hệ Thống Phân Loại Rác Thải")
    root.geometry("400x250") # Cài đặt kích thước cửa sổ
    
    # Tiêu đề
    label_title = tk.Label(root, text="CHỌN PHƯƠNG THỨC LẤY ẢNH", font=("Arial", 14, "bold"))
    label_title.pack(pady=20)
    
    # NÚT BẤM 1: Lấy ảnh từ thiết bị
    btn_upload = tk.Button(root, text="Tải ảnh từ máy tính", font=("Arial", 12), width=25, height=2, bg="#4CAF50", fg="white", command=hanh_dong_tai_anh_tu_file)
    btn_upload.pack(pady=10)
    
    # NÚT BẤM 2: Sử dụng Camera
    btn_camera = tk.Button(root, text="Sử dụng Camera trực tiếp", font=("Arial", 12), width=25, height=2, bg="#2196F3", fg="white", command=hanh_dong_su_dung_camera)
    btn_camera.pack(pady=10)
    
    # Chạy vòng lặp duy trì cửa sổ
    root.mainloop()

if __name__ == "__main__":
    main()