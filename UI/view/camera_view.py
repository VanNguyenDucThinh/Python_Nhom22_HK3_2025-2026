import os
import cv2
import customtkinter as ctk
from PIL import Image

class CameraView(ctk.CTkFrame):
    def __init__(self, master, cam_id=0, switch_view_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.cam_id = int(cam_id) if str(cam_id).isdigit() else 0
        self.switch_view_callback = switch_view_callback
        self.cap = None
        self.is_running = False
        
        self._setup_ui()
        self._start_camera()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL TRÁI: CAMERA ---
        self.cam_frame = ctk.CTkFrame(self)
        self.cam_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.top_bar = ctk.CTkFrame(self.cam_frame, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=10, pady=(10, 0))

        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        assets_dir = os.path.join(current_dir, "assets")

        try:
            img_return = ctk.CTkImage(Image.open(os.path.join(assets_dir, "return.png")), size=(20, 20))
        except FileNotFoundError:
            img_return = None

        self.btn_back = ctk.CTkButton(
            self.top_bar, text=" Quay lại chọn camera", image=img_return, compound="left",
            fg_color="transparent", text_color="#495057", hover_color="#e9ecef", 
            anchor="w", command=self._go_back
        )
        self.btn_back.pack(side="left")

        self.video_label = ctk.CTkLabel(self.cam_frame, text="Đang tải Camera...", fg_color="black", corner_radius=10)
        self.video_label.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        self.btn_frame = ctk.CTkFrame(self.cam_frame, fg_color="transparent")
        self.btn_frame.pack(pady=15)

        self.btn_capture = ctk.CTkButton(
            self.btn_frame, text="[📷] Chụp Ảnh", command=self._capture_image, 
            fg_color="#00b050", hover_color="#008f40", height=40, width=150
        )
        self.btn_capture.pack(side="left", padx=10)

        self.btn_upload = ctk.CTkButton(
            self.btn_frame, text="[↑] Tải Ảnh Lên", 
            fg_color="#0d6efd", hover_color="#0b5ed7", height=40, width=150
        )
        self.btn_upload.pack(side="left", padx=10)

        # --- PANEL PHẢI: KẾT QUẢ & HƯỚNG DẪN ---
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Khung Kết quả
        self.result_frame = ctk.CTkFrame(self.right_frame, fg_color="white", corner_radius=10)
        self.result_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.result_frame, text="Kết Quả Phân Tích", font=ctk.CTkFont(size=16, weight="bold"), text_color="#102a43").pack(pady=15, anchor="w", padx=20)
        self.result_label = ctk.CTkLabel(self.result_frame, text="[📷]\nChụp hoặc tải ảnh lên để phân tích", text_color="#829ab1", justify="center")
        self.result_label.pack(pady=(20, 50))

        # Khung Hướng dẫn phân loại
        self.guide_frame = ctk.CTkFrame(self.right_frame, fg_color="#f0fdf4", border_width=1, border_color="#d1e7dd", corner_radius=10)
        self.guide_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.guide_frame, text="Hướng Dẫn Phân Loại", font=ctk.CTkFont(size=15, weight="bold"), text_color="#212529").pack(pady=(15, 10), anchor="w", padx=20)
        
        categories = [
            ("#00b050", "Hữu cơ:", "Thực phẩm, lá cây"),
            ("#0d6efd", "Vô cơ:", "Đất, gạch, đá"),
            ("#ffc107", "Tái chế:", "Nhựa, giấy, kim loại"),
            ("#dc3545", "Độc hại:", "Pin, hóa chất")
        ]

        for color, name, desc in categories:
            row = ctk.CTkFrame(self.guide_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)

            bullet = ctk.CTkFrame(row, width=16, height=16, fg_color=color, corner_radius=4)
            bullet.pack(side="left", padx=(0, 10))
            bullet.pack_propagate(False)

            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(weight="bold", size=13), text_color="#212529").pack(side="left")
            ctk.CTkLabel(row, text=f" {desc}", text_color="#495057", font=ctk.CTkFont(size=13)).pack(side="left")

    def _start_camera(self):
        self.cap = cv2.VideoCapture(self.cam_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.video_label.configure(text="Lỗi: Không kết nối được Camera!", text_color="red")
            return
        
        self.is_running = True
        self._update_frame()

    def _update_frame(self):
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv2_image)
            ctk_image = ctk.CTkImage(light_image=pil_image, size=(640, 480))
            self.video_label.configure(image=ctk_image, text="")
        
        self.after(15, self._update_frame)

    def _capture_image(self):
        pass

    def _go_back(self):
        if self.switch_view_callback:
            self.switch_view_callback(target_view="select_cam")

    def destroy(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        super().destroy()