import sys
sys.stdout.reconfigure(encoding='utf-8')
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import threading 

from image_processor import resize_image, convert_frame_to_bytes
from api_client import upload_waste_image
from camera_handler import capture_from_webcam

def quy_trinh_xu_ly_va_gui_anh(frame):
    """Quy trình khép kín: Tiền xử lý -> Đóng gói -> Gửi API"""
    try:
        if frame is None:
            messagebox.showwarning("Thông báo", "Không nhận được dữ liệu hình ảnh!")
            return

        anh_sach = resize_image(frame)
        du_lieu_bytes = convert_frame_to_bytes(anh_sach)
        
        print("Đang gửi ảnh sang hệ thống AI để dự đoán...")
        ket_qua = upload_waste_image(du_lieu_bytes)
        
        # Kiểm tra dữ liệu trả về chuẩn xác
        if isinstance(ket_qua, dict):
            if ket_qua.get("status") == "success":
                nhan_rac = ket_qua.get("label", "Không rõ")
                do_chinh_xac = ket_qua.get("confidence", "0%")
                thong_bao = f"🏷️ Loại rác nhận diện: {nhan_rac}\n🎯 Độ tin cậy: {do_chinh_xac}"
                messagebox.showinfo("KẾT QUẢ PHÂN LOẠI", thong_bao)
            else:
                loi_nhan = ket_qua.get("message", "Lỗi không xác định từ AI Service")
                messagebox.showwarning("Thông báo hệ thống", f"AI phản hồi: {loi_nhan}")
        else:
            messagebox.showerror("Lỗi kết nối", f"Server phản hồi sai định dạng:\n{ket_qua}")
        
    except Exception as e:
        messagebox.showerror("Lỗi hệ thống", f"Có lỗi xảy ra trong quá trình xử lý: {e}")

def hanh_dong_tai_anh_tu_file():
    """Xử lý tải ảnh từ máy tính chạy ngầm để không đơ UI"""
    duong_dan_anh = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    
    if duong_dan_anh:
        def luong_xu_ly_anh_upload():
            frame = cv2.imread(duong_dan_anh)
            if frame is not None:
                quy_trinh_xu_ly_va_gui_anh(frame)
            else:
                messagebox.showerror("Lỗi đọc file", "Hệ thống không thể mở file ảnh này!")
                
        threading.Thread(target=luong_xu_ly_anh_upload, daemon=True).start()

def hanh_dong_su_dung_camera():
    """Bật luồng Camera chạy song song với UI"""
    threading.Thread(target=capture_from_webcam, args=(quy_trinh_xu_ly_va_gui_anh,), daemon=True).start()

def main():
    root = tk.Tk()
    root.title("Hệ Thống Phân Loại Rác Thải")
    
    window_width = 600
    window_height = 450
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}') 
    
    # ĐÃ SỬA: Xóa bỏ hoàn toàn ký tự gạch chéo ngược gây lỗi cú pháp
    label_title = tk.Label(root, text="CHỌN PHƯƠNG THỨC LẤY ẢNH", font=("Arial", 16, "bold"))
    label_title.pack(pady=40)
    
    btn_upload = tk.Button(
        root, 
        text="TẢI ẢNH TỪ MÁY TÍNH", 
        command=hanh_dong_tai_anh_tu_file, 
        width=30, 
        height=2, 
        bg="#3498db", 
        fg="white", 
        font=("Arial", 11, "bold")
    )
    btn_upload.pack(pady=15)
    
    btn_camera = tk.Button(
        root, 
        text="SỬ DỤNG WEBCAM TRỰC TIẾP", 
        command=hanh_dong_su_dung_camera, 
        width=30, 
        height=2, 
        bg="#2ecc71", 
        fg="white", 
        font=("Arial", 11, "bold")
    )
    btn_camera.pack(pady=15)
    
    root.mainloop()

if __name__ == '__main__':
    main()