import sys
import os
from PIL import Image
import customtkinter as ctk
from data_frame import DataFrameView

# Them duong dan goc de goi cheo thu muc
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from view.select_cam_view import SelectCamView
from view.camera_view import CameraView

ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("green")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Hệ thống Phân loại Rác thải")
        self.geometry("1000x700")
        self.minsize(800, 600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        self._setup_header()

        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        self.show_select_cam_view()

    def _setup_header(self):
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=15)

        assets_dir = os.path.join(current_dir, "assets")

        try:
            img_logo = ctk.CTkImage(Image.open(os.path.join(assets_dir, "logo.png")), size=(24, 24))
            img_cam = ctk.CTkImage(Image.open(os.path.join(assets_dir, "camera.png")), size=(20, 20))
            img_data = ctk.CTkImage(Image.open(os.path.join(assets_dir, "database.png")), size=(20, 20))
        except FileNotFoundError:
            img_logo = img_cam = img_data = None

        self.logo_label = ctk.CTkLabel(
            self.header_frame, text=" Phân Loại Rác", image=img_logo,
            compound="left", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(side="left")

        self.btn_dashboard = ctk.CTkButton(
            self.header_frame, text=" Dữ Liệu", image=img_data, compound="left",
            command=self.show_data_frame_view,
            fg_color="#f1f3f5", text_color="#212529", hover_color="#e2e6ea", width=120, height=35
        )
        self.btn_dashboard.pack(side="right", padx=(15, 0))

        self.btn_camera = ctk.CTkButton(
            self.header_frame, text=" Camera", image=img_cam, compound="left",
            command=self.show_select_cam_view,
            fg_color="#00b050", text_color="white", hover_color="#008f40", width=120, height=35
        )
        self.btn_camera.pack(side="right")

        self.separator = ctk.CTkFrame(self, height=1, fg_color="#dee2e6")
        self.separator.grid(row=1, column=0, sticky="ew")
        
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def switch_view(self, target_view, **kwargs):
        if target_view == "camera_view":
            self.show_camera_view(kwargs.get("selected_cam_id"))
        elif target_view == "select_cam":
            self.show_select_cam_view()
        elif target_view == "data_frame":
            self.show_data_frame_view()

    def show_select_cam_view(self):
        self.clear_main_frame()
        view = SelectCamView(self.main_frame, switch_view_callback=self.switch_view)
        view.pack(fill="both", expand=True)

    def show_camera_view(self, cam_id=0):
        self.clear_main_frame()
        view = CameraView(self.main_frame, cam_id=cam_id, switch_view_callback=self.switch_view)
        view.pack(fill="both", expand=True)

    def show_dashboard_view(self):
        self.clear_main_frame()
        label = ctk.CTkLabel(self.main_frame, text="[Dashboard View]", font=("Arial", 20))
        label.pack(expand=True)
    
    def show_data_frame_view(self):
        self.clear_main_frame()
        # Tùy thuộc vào thiết kế của DataFrameView có yêu cầu tham số nào không
        # Theo code của bạn, nó nhận parent (self.main_frame)
        view = DataFrameView(self.main_frame)
        view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()