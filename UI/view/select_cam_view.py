import customtkinter as ctk

class SelectCamView(ctk.CTkFrame):
    def __init__(self, master, switch_view_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.switch_view_callback = switch_view_callback
        self._setup_ui()

    def _setup_ui(self):
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True)

        self.icon_label = ctk.CTkLabel(self.center_frame, text="[📷]", font=ctk.CTkFont(size=40))
        self.icon_label.pack(pady=(0, 10))

        self.title_label = ctk.CTkLabel(self.center_frame, text="Chọn Camera", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(0, 5))

        self.subtitle_label = ctk.CTkLabel(self.center_frame, text="Chọn camera bạn muốn sử dụng để phân loại rác", text_color="gray")
        self.subtitle_label.pack(pady=(0, 30))

        self._render_camera_options()

    def _render_camera_options(self):
        # TODO: Tích hợp logic detect thiết bị ngoại vi bằng OpenCV
        mock_camera_list = [
            {"name": "Camera mặc định", "id": "0"},
            {"name": "Camera trước", "id": "1"},
            {"name": "Camera sau", "id": "2"}
        ]

        for cam in mock_camera_list:
            cam_btn = ctk.CTkButton(
                self.center_frame, 
                text=f"{cam['name']}\nID: {cam['id']}", 
                height=60, width=400, corner_radius=10,
                fg_color="#f8f9fa", text_color="#212529", hover_color="#e9ecef",
                anchor="w",
                command=lambda c=cam['id']: self._handle_camera_select(c)
            )
            cam_btn.pack(pady=8)

    def _handle_camera_select(self, cam_id):
        if self.switch_view_callback:
            self.switch_view_callback(target_view="camera_view", selected_cam_id=cam_id)