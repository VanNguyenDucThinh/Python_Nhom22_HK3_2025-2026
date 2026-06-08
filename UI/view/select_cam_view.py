import os
import cv2
import threading
import customtkinter as ctk
from PIL import Image

class SelectCamView(ctk.CTkFrame):
    def __init__(self, master, switch_view_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.switch_view_callback = switch_view_callback
        self._setup_ui()

    def _setup_ui(self):
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True)

        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        assets_dir = os.path.join(current_dir, "assets")

        try:
            img_cam_large = ctk.CTkImage(Image.open(os.path.join(assets_dir, "camera.png")), size=(48, 48))
            self.img_cam_small = ctk.CTkImage(Image.open(os.path.join(assets_dir, "camera.png")), size=(24, 24))
        except FileNotFoundError:
            img_cam_large = self.img_cam_small = None

        self.icon_label = ctk.CTkLabel(self.center_frame, text="" if img_cam_large else "[📷]", image=img_cam_large)
        self.icon_label.pack(pady=(0, 10))

        self.title_label = ctk.CTkLabel(self.center_frame, text="Chọn Camera", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(0, 5))

        self.subtitle_label = ctk.CTkLabel(self.center_frame, text="Chọn camera bạn muốn sử dụng để phân loại rác", text_color="gray")
        self.subtitle_label.pack(pady=(0, 15))

        # --- NÚT TÍNH NĂNG MỚI: QUÉT THIẾT BỊ ---
        self.btn_scan = ctk.CTkButton(
            self.center_frame,
            text="Quét thiết bị",
            width=150, height=35,
            fg_color="#6c757d", hover_color="#5a6268",
            command=self._start_scan_thread
        )
        self.btn_scan.pack(pady=(0, 20))

        # Khung chứa danh sách các camera
        self.options_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.options_frame.pack(fill="both", expand=True)

        # Mặc định load cực nhanh chỉ với Camera 0
        self._show_default_camera()

    def _show_default_camera(self):
        """Khởi tạo nhanh danh sách chỉ với Camera mặc định của máy."""
        self._clear_options()
        default_cam = [{"name": "Camera Mặc Định", "id": "0"}]
        self._render_camera_options(default_cam)

    def _start_scan_thread(self):
        """Xử lý sự kiện bấm nút quét phần cứng."""
        # Khóa nút bấm ngay lập tức để chặn người dùng spam click gây lỗi
        self.btn_scan.configure(state="disabled", text="Đang quét...")
        self.subtitle_label.configure(text="Đang tìm kiếm thiết bị phần cứng, vui lòng đợi...", text_color="#0d6efd")
        
        self._clear_options()
        self.update_idletasks() 
        
        # Gọi luồng ngầm thực thi
        threading.Thread(target=self._scan_cameras_worker, daemon=True).start()

    def _scan_cameras_worker(self):
        """Luồng ngầm quét cổng vật lý."""
        camera_list = self._detect_available_cameras()
        self.after(0, lambda: self._on_scan_complete(camera_list))

    def _on_scan_complete(self, camera_list):
        """Mở khóa giao diện và hiển thị kết quả."""
        self.btn_scan.configure(state="normal", text="Quét thiết bị")
        self.subtitle_label.configure(text="Chọn camera bạn muốn sử dụng để phân loại rác", text_color="gray")
        self._render_camera_options(camera_list)

    def _detect_available_cameras(self):
        available_cams = []
        for i in range(4):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                name = "Camera Máy Tính" if i == 0 else f"Camera Rời (Cổng {i})"
                available_cams.append({"name": name, "id": str(i)})
                cap.release()
        return available_cams

    def _render_camera_options(self, camera_list):
        if not camera_list:
            self.subtitle_label.configure(text="Không tìm thấy camera nào kết nối với máy tính!", text_color="red")
            return

        for cam in camera_list:
            cam_btn = ctk.CTkButton(
                self.options_frame, 
                text=f" {cam['name']}\n ID: {cam['id']}", 
                image=self.img_cam_small, compound="left",
                height=60, width=400, corner_radius=10,
                fg_color="#f8f9fa", text_color="#212529", hover_color="#e9ecef", anchor="w",
                command=lambda c=cam['id']: self._handle_camera_select(c)
            )
            cam_btn.pack(pady=8)

    def _clear_options(self):
        """Hàm dọn dẹp danh sách nút bấm cũ."""
        for widget in self.options_frame.winfo_children():
            widget.destroy()

    def _handle_camera_select(self, cam_id):
        if self.switch_view_callback:
            self.switch_view_callback(target_view="camera_view", selected_cam_id=cam_id)