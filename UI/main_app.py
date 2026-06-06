import customtkinter as ctk

# Cài đặt giao diện mặc định
ctk.set_appearance_mode("System")  # Tự động theo giao diện Sáng/Tối của Windows
ctk.set_default_color_theme("green")  # Tông màu xanh lá chủ đạo như Figma

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Cấu hình cửa sổ chính
        self.title("Hệ thống Phân loại Rác thải - Nhóm 22")
        self.geometry("1000x700")
        self.minsize(800, 600)

        # Tạo một khung chính (Container) để chứa các màn hình (Views)
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # TODO: Sẽ nhúng các màn hình views vào đây sau

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()