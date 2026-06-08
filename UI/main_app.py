import customtkinter as ctk
from data_frame import DataFrameView
from PIL import Image
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Cấu hình cửa sổ chính rộng rãi chuẩn UI
        self.title("Hệ thống Phân loại Rác thải - Nhóm 22")
        self.geometry("1250x820")  
        self.minsize(1050, 750)
        self.configure(fg_color="#f8f9fa")

        # --- XỬ LÝ ĐƯỜNG DẪN ẢNH VÀ ICON ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "logo")

        try:
            # Tải bộ ảnh gốc (Màu đen/tối)
            img_camera_dark = Image.open(os.path.join(logo_path, "camera_icon.png"))
            img_data_dark = Image.open(os.path.join(logo_path, "data_icon.png"))
            
            # Tải bộ ảnh mới (Màu trắng)
            img_camera_white = Image.open(os.path.join(logo_path, "camera_white.png"))
            img_data_white = Image.open(os.path.join(logo_path, "data_white.png"))

            # Định kích thước icon cân xứng với chữ to
            self.icon_camera_w = ctk.CTkImage(light_image=img_camera_white, size=(22, 22))
            self.icon_camera_d = ctk.CTkImage(light_image=img_camera_dark, size=(22, 22))
            self.icon_data_w = ctk.CTkImage(light_image=img_data_white, size=(22, 22))
            self.icon_data_d = ctk.CTkImage(light_image=img_data_dark, size=(22, 22))
            
            # Icon camera trắng cố định dành cho hộp Logo xanh bên trái
            self.icon_logo_main = ctk.CTkImage(light_image=img_camera_white, size=(26, 26))
        except Exception as e:
            print(f"Lưu ý: Thiếu file ảnh icon trong thư mục logo ({e})")
            self.icon_camera_w = self.icon_camera_d = self.icon_data_w = self.icon_data_d = self.icon_logo_main = None

        # 1. THANH TOPBAR ĐIỀU HƯỚNG
        self.header = ctk.CTkFrame(self, height=90, fg_color="white", corner_radius=0)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        # --- CỤM LOGO GÓC TRÁI (Ô vuông xanh lá + Chữ Phân Loại Rác to rõ) ---
        self.logo_container = ctk.CTkFrame(self.header, fg_color="transparent")
        self.logo_container.pack(side="left", padx=40)

        self.logo_icon_box = ctk.CTkLabel(
            self.logo_container, text="", image=self.icon_logo_main,
            fg_color="#00a843", width=52, height=52, corner_radius=12
        )
        self.logo_icon_box.pack(side="left", padx=(0, 15))

        # TĂNG CỠ CHỮ: "Phân Loại Rác" lên cỡ 28 cực kỳ nổi bật
        self.lbl_title = ctk.CTkLabel(self.logo_container, text="Phân Loại Rác", font=("Arial", 28, "bold"), text_color="black")
        self.lbl_title.pack(side="left")
        # --- CẶP NÚT BẤM ĐIỀU HƯỚNG BÊN PHẢI ---
        # Nút Dữ Liệu
        self.btn_data = ctk.CTkButton(
            self.header, text="  Dữ Liệu", image=self.icon_data_d, compound="left",
            width=150, height=48, font=("Arial", 16, "bold"), corner_radius=10,
            command=lambda: self.switch_tab("data")
        )
        self.btn_data.pack(side="right", padx=(10, 40), pady=20)
        
        # Nút Camera
        self.btn_camera = ctk.CTkButton(
            self.header, text="  Camera", image=self.icon_camera_d, compound="left",
            width=150, height=48, font=("Arial", 16, "bold"), corner_radius=10,
            command=lambda: self.switch_tab("camera")
        )
        self.btn_camera.pack(side="right", padx=10, pady=20)

        # 2. KHUNG CONTAINER CHỨA NỘI DUNG MÀN HÌNH CON
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=40, pady=25)
        
        # Mặc định load giao diện Quản lý dữ liệu trước
        self.switch_tab("data")

    def switch_tab(self, tab_name):
        # TRẠNG THÁI HOVER / KHÔNG ĐƯỢC CHỌN: Chỉ hiện màu xám nhẹ, KHÔNG hiện xanh lá
        self.btn_data.configure(fg_color="#f0f2f5", text_color="black", image=self.icon_data_d, hover_color="#e4e6e9")
        self.btn_camera.configure(fg_color="#f0f2f5", text_color="black", image=self.icon_camera_d, hover_color="#e4e6e9")
        
        # Xóa nội dung cũ trong container
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # TRẠNG THÁI ĐƯỢC CHỌN: Đổi sang nền xanh lá, chữ trắng, icon trắng
        if tab_name == "data":
            self.btn_data.configure(fg_color="#00a843", text_color="white", image=self.icon_data_w, hover_color="#00a843")
            DataFrameView(self.container).pack(fill="both", expand=True)
        elif tab_name == "camera":
            self.btn_camera.configure(fg_color="#00a843", text_color="white", image=self.icon_camera_w, hover_color="#00a843")
            
            # TĂNG CỠ CHỮ: Chữ thông báo camera lên cỡ 20
            lbl_placeholder = ctk.CTkLabel(
                self.container, 
                text="📷 Khung hình camera của bạn cùng nhóm sẽ hiển thị tại đây", 
                font=("Arial", 20, "italic"), text_color="gray"
            )
            lbl_placeholder.pack(expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()