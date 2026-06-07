import os
import cv2
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

        self.subtitle_label = ctk.CTkLabel(self.center_frame, text="Đang quét thiết bị...", text_color="gray")
        self.subtitle_label.pack(pady=(0, 30))

        # Ép UI render dòng text "Đang quét..." trước khi chạy vòng lặp nặng
        self.update_idletasks()
        self._render_camera_options()

    def _render_camera_options(self):
        camera_list = self._detect_available_cameras()

        if not camera_list:
            self.subtitle_label.configure(text="Không tìm thấy camera nào kết nối với máy tính!", text_color="red")
            return

        self.subtitle_label.configure(text="Chọn camera bạn muốn sử dụng để phân loại rác", text_color="gray")

        for cam in camera_list:
            cam_btn = ctk.CTkButton(
                self.center_frame, 
                text=f" {cam['name']}\n ID: {cam['id']}", 
                image=self.img_cam_small, compound="left",
                height=60, width=400, corner_radius=10,
                fg_color="#f8f9fa", text_color="#212529", hover_color="#e9ecef", anchor="w",
                command=lambda c=cam['id']: self._handle_camera_select(c)
            )
            cam_btn.pack(pady=8)

    def _detect_available_cameras(self):
        """Quét các cổng camera đang hoạt động."""
        available_cams = []
        for i in range(4):
            # Dùng CAP_DSHOW để quét nhanh, không bị treo
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                name = "Camera Máy Tính" if i == 0 else f"Camera Rời (Cổng {i})"
                available_cams.append({"name": name, "id": str(i)})
                cap.release()
        return available_cams

    def _handle_camera_select(self, cam_id):
        if self.switch_view_callback:
            self.switch_view_callback(target_view="camera_view", selected_cam_id=cam_id)