import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

# =========================================================================
# XỬ LÝ ĐƯỜNG DẪN: Giúp file trong folder UI gọi được các file ở thư mục gốc
# =========================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# Bây giờ import các file xử lý logic cũ từ thư mục gốc một cách an toàn
try:
    import cv2
    import customtkinter as ctk
    from PIL import Image, ImageTk
    from image_processor import resize_image, convert_frame_to_bytes
    from api_client import upload_waste_image
except ImportError as e:
    print(f"[LỖI THƯ VIỆN]: Thiếu thư viện hoặc file liên quan. Chi tiết: {e}")
    print("👉 Hãy chắc chắn đã chạy lệnh: pip install customtkinter pillow opencv-python requests")
    sys.exit(1)

# Cấu hình giao diện Hệ thống bo góc hiện đại
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class WasteApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HỆ THỐNG QUẢN LÝ VÀ PHÂN LOẠI RÁC THẢI THÔNG MINH")
        self.geometry("1000x650")
        self.resizable(False, False)

        # Quản lý luồng Camera Laptop
        self.cap = None
        self.camera_running = False

        # Container chính chứa các tầng giao diện
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.dashboard_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.camera_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")

        self.build_dashboard_screen()
        self.build_camera_screen()
        self.show_dashboard()

    # =========================================================================
    # GIAO DIỆN MÀN HÌNH 1: DASHBOARD THỐNG KÊ (ẢNH 1)
    # =========================================================================
    def build_dashboard_screen(self):
        top_bar = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 15))
        
        title_lbl = ctk.CTkLabel(top_bar, text="📊 THỐNG KÊ DỮ LIỆU RÁC THẢI", font=ctk.CTkFont(size=22, weight="bold"))
        title_lbl.pack(side="left")
        
        btn_go_cam = ctk.CTkButton(top_bar, text="📸 Chuyển Sang Camera", command=self.show_camera, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(weight="bold"))
        btn_go_cam.pack(side="right")

        stats_grid = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        stats_grid.pack(fill="x", pady=10)
        stats_grid.grid_columnconfigure((0, 1, 2, 3), weight=1, pad=15)

        # 4 Ô màu tương ứng 4 loại rác (Số liệu tạm thời - Sau này sẽ truy vấn DB)
        self.create_stat_box(stats_grid, 0, "Rác Hữu Cơ", "12 Lượt", "#43a047")
        self.create_stat_box(stats_grid, 1, "Rác Tái Chế", "45 Lượt", "#1e88e5")
        self.create_stat_box(stats_grid, 2, "Rác Vô Cơ", "08 Lượt", "#f4511e")
        self.create_stat_box(stats_grid, 3, "Rác Độc Hại", "02 Lượt", "#e53935")

        history_title = ctk.CTkLabel(self.dashboard_frame, text="📋 Phân Tích Lịch Sử Gần Đây", font=ctk.CTkFont(size=16, weight="bold"))
        history_title.pack(anchor="w", pady=(20, 5))

        table_frame = ctk.CTkFrame(self.dashboard_frame)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "time", "type", "conf")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID Bản Ghi")
        self.tree.heading("time", text="Thời Gian Thu Nhận")
        self.tree.heading("type", text="Phân Loại Rác")
        self.tree.heading("conf", text="Độ Tin Cậy")
        
        self.tree.column("id", width=100, anchor="center")
        self.tree.column("time", width=250, anchor="center")
        self.tree.column("type", width=200, anchor="center")
        self.tree.column("conf", width=150, anchor="center")

        # Mock Data mẫu lịch sử giống history_database
        self.tree.insert("", "end", values=("#102", "2026-06-06 21:14:02", "Rác tái chế", "94.50%"))
        self.tree.insert("", "end", values=("#101", "2026-06-06 18:32:15", "Rác hữu cơ", "88.20%"))

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_stat_box(self, parent, column, title, value, color):
        box = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=100)
        box.grid(row=0, column=column, sticky="nsew", padx=5)
        box.grid_propagate(False)
        
        lbl_title = ctk.CTkLabel(box, text=title, text_color="white", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_title.pack(pady=(15, 2))
        lbl_val = ctk.CTkLabel(box, text=value, text_color="white", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_val.pack()

    # =========================================================================
    # GIAO DIỆN MÀN HÌNH 2 & 3: KHÔNG GIAN CAMERA TRÌNH CHIẾU & KẾT QUẢ
    # =========================================================================
    def build_camera_screen(self):
        top_bar = ctk.CTkFrame(self.camera_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 15))
        
        title_lbl = ctk.CTkLabel(top_bar, text="📸 KHÔNG GIAN QUÉT CAMERA", font=ctk.CTkFont(size=22, weight="bold"))
        title_lbl.pack(side="left")
        
        btn_go_data = ctk.CTkButton(top_bar, text="📊 Xem Số Liệu Hệ Thống", command=self.show_dashboard, fg_color="#3498db", hover_color="#2980b9", font=ctk.CTkFont(weight="bold"))
        btn_go_data.pack(side="right")

        workspace = ctk.CTkFrame(self.camera_frame, fg_color="transparent")
        workspace.pack(fill="both", expand=True)

        # Màn hình đen trình chiếu / Camera Laptop
        self.video_container = ctk.CTkFrame(workspace, fg_color="#1e1e1e", corner_radius=12)
        self.video_container.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.cam_label = ctk.CTkLabel(self.video_container, text="MÀN HÌNH TRÌNH CHIẾU / CAMERA TRỐNG\n\n(Bật Camera hoặc Tải ảnh lên)", text_color="#7f8c8d", font=ctk.CTkFont(size=14))
        self.cam_label.pack(fill="both", expand=True)

        # Ô kết quả phân tích tinh chỉnh gọn gàng (Không bị lỗi hiển thị)
        result_panel = ctk.CTkFrame(workspace, width=320, fg_color="#2c3e50", corner_radius=12)
        result_panel.pack(side="right", fill="y")
        result_panel.pack_propagate(False)

        panel_title = ctk.CTkLabel(result_panel, text="🎯 KẾT QUẢ PHÂN TÍCH", text_color="white", font=ctk.CTkFont(size=16, weight="bold"))
        panel_title.pack(pady=20)

        self.res_label_title = ctk.CTkLabel(result_panel, text="LOẠI RÁC NHẬN DIỆN:", text_color="#bdc3c7", font=ctk.CTkFont(size=12))
        self.res_label_title.pack(pady=(10, 0))
        
        self.res_label_val = ctk.CTkLabel(result_panel, text="Chờ quét dữ liệu...", text_color="#f1c40f", font=ctk.CTkFont(size=22, weight="bold"))
        self.res_label_val.pack(pady=5)

        self.res_conf_title = ctk.CTkLabel(result_panel, text="ĐỘ TIN CẬY (CONFIDENCE):", text_color="#bdc3c7", font=ctk.CTkFont(size=12))
        self.res_conf_title.pack(pady=(20, 0))
        
        self.res_conf_val = ctk.CTkLabel(result_panel, text="0.00%", text_color="#e74c3c", font=ctk.CTkFont(size=18, weight="bold"))
        self.res_conf_val.pack(pady=5)

        btn_area = ctk.CTkFrame(result_panel, fg_color="transparent")
        btn_area.pack(side="bottom", fill="x", padx=15, pady=20)

        self.btn_toggle_cam = ctk.CTkButton(btn_area, text="🎥 Bật Camera Laptop", command=self.toggle_camera, fg_color="#1abc9c", hover_color="#16a085")
        self.btn_toggle_cam.pack(fill="x", pady=5)

        # NÚT CHỤP VÀ GỬI ĐẾN AI SERVICE PHÂN TÍCH
        self.btn_capture_ai = ctk.CTkButton(btn_area, text="🎯 Chụp & Phân Tích AI", command=self.trigger_ai_detection, fg_color="#e67e22", hover_color="#d35400", state="disabled")
        self.btn_capture_ai.pack(fill="x", pady=5)

        btn_upload = ctk.CTkButton(btn_area, text="📁 Tải Ảnh Từ Thiết Bị", command=self.upload_local_image, fg_color="#9b59b6", hover_color="#8e44ad")
        btn_upload.pack(fill="x", pady=5)

    # =========================================================================
    # HÀM LOGIC XỬ LÝ KẾT NỐI CAMERA & GỬI API THẬT
    # =========================================================================
    def show_dashboard(self):
        self.stop_camera_stream()
        self.camera_frame.pack_forget()
        self.dashboard_frame.pack(fill="both", expand=True)

    def show_camera(self):
        self.dashboard_frame.pack_forget()
        self.camera_frame.pack(fill="both", expand=True)

    def toggle_camera(self):
        if not self.camera_running:
            self.cap = cv2.VideoCapture(0) # Camera trước mặc định Laptop
            if not self.cap.isOpened():
                messagebox.showerror("Lỗi", "Không thể truy cập camera laptop!")
                return
            self.camera_running = True
            self.btn_toggle_cam.configure(fg_color="#e74c3c", hover_color="#c0392b", text="🛑 Tắt Camera")
            self.btn_capture_ai.configure(state="normal")
            self.update_camera_stream()
        else:
            self.stop_camera_stream()

    def update_camera_stream(self):
        if self.camera_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy() # Lưu trữ khung hình hiện tại để chụp ảnh gửi AI
                cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(cv2_img).resize((600, 440))
                tk_img = ImageTk.PhotoImage(image=pil_img)
                
                self.cam_label.configure(image=tk_img, text="")
                self.cam_label.image = tk_img
            self.after(15, self.update_camera_stream)

    def stop_camera_stream(self):
        self.camera_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.btn_toggle_cam.configure(fg_color="#1abc9c", hover_color="#16a085", text="🎥 Bật Camera Laptop")
        self.btn_capture_ai.configure(state="disabled")
        self.cam_label.configure(image="", text="MÀN HÌNH TRÌNH CHIẾU / CAMERA TRỐNG\n\n(Bật Camera hoặc Tải ảnh lên)")

    def trigger_ai_detection(self):
        """Chụp frame hiện tại trên camera và gửi sang AI_Service (Chống treo UI bằng Thread)"""
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            self.res_label_val.configure(text="AI đang tính toán...", text_color="#f1c40f")
            threading.Thread(target=self._run_api_process, args=(self.current_frame,), daemon=True).start()

    def upload_local_image(self):
        """Tải ảnh từ máy tính lên khung đen trình chiếu và gửi đi phân tích"""
        self.stop_camera_stream()
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            frame = cv2.imread(file_path)
            if frame is not None:
                # Vẽ ảnh lên màn hình giao diện chính
                pil_img = Image.open(file_path).resize((600, 440))
                tk_img = ImageTk.PhotoImage(image=pil_img)
                self.cam_label.configure(image=tk_img, text="")
                self.cam_label.image = tk_img
                
                self.res_label_val.configure(text="AI đang tính toán...", text_color="#f1c40f")
                # Kích hoạt luồng chạy ngầm gửi API
                threading.Thread(target=self._run_api_process, args=(frame,), daemon=True).start()

    def _run_api_process(self, frame):
        """Hàm gửi dữ liệu nhị phân sang API xử lý"""
        try:
            anh_sach = resize_image(frame)
            du_lieu_bytes = convert_frame_to_bytes(anh_sach)
            
            # Gọi hàm trong api_client.py kết nối tới cổng 8000 của AI Service
            ket_qua = upload_waste_image(du_lieu_bytes)
            
            if isinstance(ket_qua, dict) and ket_qua.get("status") == "success":
                label = ket_qua.get("label", "Không rõ")
                conf = ket_qua.get("confidence", "0.00%")
                
                # Cập nhật kết quả phân tích lên ô panel bên phải giao diện
                self.res_label_val.configure(text=label.upper(), text_color="#2ecc71")
                self.res_conf_val.configure(text=conf, text_color="#2ecc71")
            else:
                self.res_label_val.configure(text="Lỗi kết nối AI!", text_color="#e74c3c")
        except Exception as e:
            self.res_label_val.configure(text="Lỗi hệ thống!", text_color="#e74c3c")

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        
    app = WasteApp()
    app.mainloop()