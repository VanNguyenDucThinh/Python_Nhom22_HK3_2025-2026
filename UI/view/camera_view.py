import cv2
import customtkinter as ctk
from PIL import Image

class CameraView(ctk.CTkFrame):
    """
    View component hiển thị luồng video từ camera và kết quả phân tích.
    Tích hợp OpenCV để đọc frame liên tục và hiển thị qua CTkImage.
    """
    def __init__(self, master, cam_id=0, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Khởi tạo state cho camera
        self.cam_id = int(cam_id) if str(cam_id).isdigit() else 0
        self.cap = None
        self.is_running = False
        
        self._setup_ui()
        self._start_camera()

    def _setup_ui(self):
        """Khởi tạo layout tĩnh."""
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL TRÁI: CAMERA ---
        self.cam_frame = ctk.CTkFrame(self)
        self.cam_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.video_label = ctk.CTkLabel(self.cam_frame, text="Đang tải Camera...", fg_color="black")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        self.btn_frame = ctk.CTkFrame(self.cam_frame, fg_color="transparent")
        self.btn_frame.pack(pady=15)

        self.btn_capture = ctk.CTkButton(
            self.btn_frame, text="Chụp Ảnh", command=self._capture_image, 
            fg_color="#28a745", hover_color="#218838"
        )
        self.btn_capture.pack(side="left", padx=10)

        self.btn_upload = ctk.CTkButton(
            self.btn_frame, text="Tải Ảnh Lên", 
            fg_color="#0d6efd", hover_color="#0b5ed7"
        )
        self.btn_upload.pack(side="left", padx=10)

        # --- PANEL PHẢI: KẾT QUẢ ---
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.result_frame = ctk.CTkFrame(self.right_frame)
        self.result_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.result_frame, text="Kết Quả Phân Tích", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, anchor="w", padx=15)
        
        self.result_label = ctk.CTkLabel(self.result_frame, text="Chụp hoặc tải ảnh lên để phân tích", text_color="gray")
        self.result_label.pack(pady=50)

        self.guide_frame = ctk.CTkFrame(self.right_frame)
        self.guide_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.guide_frame, text="[Placeholder: Component Hướng dẫn]").pack(expand=True)

    def _start_camera(self):
        """Mở kết nối thiết bị và khởi động vòng lặp render."""
        self.cap = cv2.VideoCapture(self.cam_id)
        if not self.cap.isOpened():
            self.video_label.configure(text="Không thể kết nối với Camera!", text_color="red")
            return
        
        self.is_running = True
        self._update_frame()

    def _update_frame(self):
        """Đọc frame từ OpenCV và render lên GUI mỗi 15ms."""
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if ret:
            # Chuyển đổi định dạng màu BGR -> RGB
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv2_image)
            
            # TODO: Cập nhật size động theo kích thước label (nếu cần)
            ctk_image = ctk.CTkImage(light_image=pil_image, size=(640, 480))
            self.video_label.configure(image=ctk_image, text="")
        
        # Đệ quy gọi lại hàm bằng after() thay vì while True
        self.after(15, self._update_frame)

    def _capture_image(self):
        """Xử lý sự kiện lấy frame hiện tại gửi qua API."""
        # TODO: Lấy frame đang hiển thị, encode base64 hoặc bytes và post request
        pass

    def destroy(self):
        """Lifecycle hook: Giải phóng tài nguyên camera khi view bị hủy."""
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        super().destroy()
