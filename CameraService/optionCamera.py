# option_camera.py
import tkinter as tk
from tkinter import messagebox

class CameraOptionPopup:
    """Class chuyên biệt thực hiện nhiệm vụ hiển thị giao diện chọn ID Camera"""
    def __init__(self, root_window, on_id_selected_callback):
        self.root = root_window
        self.callback = on_id_selected_callback
        
        # Cấu hình cửa sổ popup
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Cấu hình Camera")
        self.popup.resizable(False, False)
        
        # Căn giữa popup theo tọa độ của cửa sổ chính (nơi được click)
        self._center_popup(width=340, height=180)
        
        # Ép popup luôn ở trên cùng và khóa tương tác với cửa sổ mẹ
        self.popup.transient(self.root)
        self.popup.grab_set()
        
        # Khởi tạo giao diện các nút bấm
        self._create_widgets()

    def _center_popup(self, width, height):
        """Hàm nội bộ để tính toán tọa độ căn giữa theo cửa sổ chính"""
        self.root.update_idletasks()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        
        pos_x = root_x + (root_width // 2) - (width // 2)
        pos_y = root_y + (root_height // 2) - (height // 2)
        self.popup.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def _create_widgets(self):
        """Hàm nội bộ xây dựng các phần tử giao diện bên trong popup"""
        label = tk.Label(self.popup, text="CHỌN CAMERA SỬ DỤNG", font=("Arial", 11, "bold"))
        label.pack(pady=15)
        
        # Khung chứa các nút bấm nhanh
        btn_frame = tk.Frame(self.popup)
        btn_frame.pack(pady=5)
        
        btn_cam0 = tk.Button(btn_frame, text="Camera 0\n(Webcam PC)", width=12, height=2, bg="#E1E1E1", 
                             command=lambda: self._confirm_selection(0))
        btn_cam0.grid(row=0, column=0, padx=5)
        
        btn_cam1 = tk.Button(btn_frame, text="Camera 1\n(DroidCam USB)", width=12, height=2, bg="#FF9800", fg="white", 
                             command=lambda: self._confirm_selection(1))
        btn_cam1.grid(row=0, column=1, padx=5)
        
        # Khung chứa ô nhập số tùy chỉnh
        custom_frame = tk.Frame(self.popup)
        custom_frame.pack(pady=12)
        
        tk.Label(custom_frame, text="Nhập ID khác:").grid(row=0, column=0)
        self.entry_id = tk.Entry(custom_frame, width=6, justify="center")
        self.entry_id.grid(row=0, column=1, padx=5)
        
        btn_ok = tk.Button(custom_frame, text="OK", command=self._handle_custom_input, width=5, bg="#2196F3", fg="white")
        btn_ok.grid(row=0, column=2, padx=5)

    def _handle_custom_input(self):
        """Xử lý kiểm tra dữ liệu khi người dùng tự nhập số vào ô"""
        val_str = self.entry_id.get().strip()
        if not val_str:
            messagebox.showwarning("Nhắc nhở", "Vui lòng điền số ID Camera vào ô trống!", parent=self.popup)
            return
        try:
            val = int(val_str)
            if val < 0: raise ValueError
            self._confirm_selection(val)
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập một số nguyên dương hợp lệ!", parent=self.popup)

    def _confirm_selection(self, selected_id):
        """Đóng popup, ép UI cập nhật sạch sẽ rồi gửi ID về cho Main"""
        self.popup.destroy()
        self.root.update()
        # Kích hoạt callback truyền ID ngược về file main.py để bật thread camera
        self.callback(selected_id)