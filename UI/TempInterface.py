import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

current_file_path = os.path.abspath(__file__)
<<<<<<< HEAD

# 2. Tìm thư mục gốc của đồ án (Python_Nhom22_HK3_2025-2026)
=======
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
PROJECT_ROOT = os.path.dirname(os.path.dirname(current_file_path))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

<<<<<<< HEAD
# Import các thư viện cần thiết
try:
    import cv2
    import customtkinter as ctk
    import requests
    from PIL import Image, ImageTk
    
    # Đi từ thư mục gốc vào CameraService để lấy module
    from CameraService.image_processor import resize_image, convert_frame_to_bytes
    from CameraService.api_client import upload_waste_image
except ImportError as e:
    print(f"[LỖI THƯ VIỆN]: {e}")
    sys.exit(1)
=======
import cv2
import customtkinter as ctk
import requests
from PIL import Image, ImageTk
from CameraService.image_processor import resize_image, convert_frame_to_bytes
from CameraService.api_client import upload_waste_image
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class WasteApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HỆ THỐNG PHÂN LOẠI RÁC THẢI - TÍCH HỢP XEM ẢNH")
        self.geometry("1050x700")
        self.resizable(False, False)

        self.cap = None
        self.camera_running = False
        self.current_frame = None

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.dashboard_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.camera_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")

        self.build_dashboard_screen()
        self.build_camera_screen()
        self.show_dashboard()

    def build_dashboard_screen(self):
        top_bar = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 15))
        
        title_lbl = ctk.CTkLabel(top_bar, text="THỐNG KÊ & LỊCH SỬ QUÉT", font=ctk.CTkFont(size=22, weight="bold"))
        title_lbl.pack(side="left")
        
        btn_go_cam = ctk.CTkButton(top_bar, text="Chuyển Sang Scan Rác", command=self.show_camera, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(weight="bold"))
        btn_go_cam.pack(side="right")

        stats_grid = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        stats_grid.pack(fill="x", pady=10)
        stats_grid.grid_columnconfigure((0, 1, 2, 3), weight=1, pad=15)

        self.lbl_huuco_val = self.create_stat_box(stats_grid, 0, "Rác Hữu Cơ", "0 Lượt", "#43a047")
        self.lbl_taiche_val = self.create_stat_box(stats_grid, 1, "Rác Tái Chế", "0 Lượt", "#1e88e5")
        self.lbl_voco_val = self.create_stat_box(stats_grid, 2, "Rác Vô Cơ", "0 Lượt", "#f4511e")
        self.lbl_dochai_val = self.create_stat_box(stats_grid, 3, "Rác Độc Hại", "0 Lượt", "#e53935")

        history_bar = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        history_bar.pack(fill="x", pady=(20, 5))

        history_title = ctk.CTkLabel(history_bar, text="Danh Sách Phân Tích Lịch Sử", font=ctk.CTkFont(size=16, weight="bold"))
        history_title.pack(side="left")

<<<<<<< HEAD
        btn_detail = ctk.CTkButton(history_bar, text="Xem Chi Tiết & Ảnh", command=self.open_detail_window, fg_color="#3498db", hover_color="#2980b9", font=ctk.CTkFont(size=12, weight="bold"))
=======
        btn_detail = ctk.CTkButton(history_bar, text="🔎 Xem Chi Tiết & Ảnh", command=self.open_detail_window, fg_color="#3498db", hover_color="#2980b9", font=ctk.CTkFont(size=12, weight="bold"))
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
        btn_detail.pack(side="right", padx=10)

        btn_delete = ctk.CTkButton(history_bar, text="Xóa Bản Ghi", command=self.delete_selected_record, fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(size=12, weight="bold"))
        btn_delete.pack(side="right")

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

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_stat_box(self, parent, column, title, value, color):
        box = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=80)
        box.grid(row=0, column=column, sticky="nsew", padx=5)
        box.grid_propagate(False)
        lbl_title = ctk.CTkLabel(box, text=title, text_color="white", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_title.pack(pady=(10, 2))
        lbl_val = ctk.CTkLabel(box, text=value, text_color="white", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_val.pack()
        return lbl_val

    def load_database_records(self):
        try:
            response = requests.get("http://127.0.0.1:5000/api/records", timeout=3)
            if response.status_code == 200:
                records = response.json()
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                c_huuco, c_taiche, c_voco, c_dochai = 0, 0, 0, 0
                for r in records:
                    r_id, r_time = r.get("id"), r.get("timestamp")
                    r_label = str(r.get("label", "")).strip()
                    r_conf = r.get("confidence")
                    if "%" not in str(r_conf):
                        try: r_conf = f"{float(r_conf)*100:.2f}%"
                        except: pass

                    self.tree.insert("", "end", values=(f"#{r_id}", r_time, r_label, r_conf))
                    
                    if "hữu cơ" in r_label.lower(): c_huuco += 1
                    elif "tái chế" in r_label.lower(): c_taiche += 1
                    elif "vô cơ" in r_label.lower(): c_voco += 1
                    elif "độc hại" in r_label.lower(): c_dochai += 1

                self.lbl_huuco_val.configure(text=f"{c_huuco} Lượt")
                self.lbl_taiche_val.configure(text=f"{c_taiche} Lượt")
                self.lbl_voco_val.configure(text=f"{c_voco} Lượt")
                self.lbl_dochai_val.configure(text=f"{c_dochai} Lượt")
        except: pass

    def open_detail_window(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Thông báo", "Vui lòng chọn một bản ghi lịch sử để xem ảnh!")
            return
        
        row_values = self.tree.item(selected_item, "values")
        record_id = row_values[0].replace("#", "")

        try:
            resp = requests.get(f"http://127.0.0.1:5000/api/record/{record_id}", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                
                detail_win = ctk.CTkToplevel(self)
                detail_win.title(f"CHI TIẾT BẢN GHI {row_values[0]}")
                detail_win.geometry("500x550")
                detail_win.resizable(False, False)
                detail_win.attributes("-topmost", True)

<<<<<<< HEAD
                info_text = f"Mã bản ghi: #{data.get('id')}\n\n" \
                            f"Thời gian quét: {data.get('timestamp')}\n\n" \
                            f"Kết quả AI: {data.get('label').upper()}\n\n" \
                            f"Độ tin cậy: {data.get('confidence')}"
=======
                info_text = f"🆔 Mã bản ghi: #{data.get('id')}\n\n" \
                            f"⏰ Thời gian quét: {data.get('timestamp')}\n\n" \
                            f"🏷️ Kết quả AI: {data.get('label').upper()}\n\n" \
                            f"🎯 Độ tin cậy: {data.get('confidence')}"
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
                
                lbl_info = ctk.CTkLabel(detail_win, text=info_text, justify="left", font=ctk.CTkFont(size=13))
                lbl_info.pack(pady=15, padx=20, anchor="w")

                img_name = data.get("image_path")
<<<<<<< HEAD
                
=======
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
                UI_DIR = os.path.dirname(os.path.abspath(__file__))
                ROOT_DIR = os.path.dirname(UI_DIR)
                img_full_path = os.path.join(ROOT_DIR, "Backend", "saved_images", img_name) if img_name else ""

                img_label = ctk.CTkLabel(detail_win, text="")
                img_label.pack(pady=10)

                if img_name and os.path.exists(img_full_path):
                    pil_img = Image.open(img_full_path).resize((400, 300))
                    tk_img = ImageTk.PhotoImage(image=pil_img)
                    img_label.configure(image=tk_img)
                    img_label.image = tk_img
                else:
                    img_label.configure(text="[HÌNH ẢNH TRỐNG HOẶC ĐÃ BỊ FILE HỆ THỐNG XÓA]", text_color="red")
            else:
                messagebox.showerror("Lỗi", "Không thể lấy thông tin chi tiết từ Server.")
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không kết nối được tới Backend: {e}")

    def delete_selected_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Thông báo", "Vui lòng chọn hàng để xóa!")
            return
        row_values = self.tree.item(selected_item, "values")
        record_id = row_values[0].replace("#", "")

        if messagebox.askyesno("Xác nhận", f"Xóa vĩnh viễn bản ghi {row_values[0]}?"):
            try:
                resp = requests.delete(f"http://127.0.0.1:5000/delete-record/{record_id}", timeout=3)
                if resp.status_code == 200:
                    self.load_database_records()
            except: pass

<<<<<<< HEAD
=======
    # =========================================================================
    # GIAO DIỆN MÀN HÌNH CAMERA & NÚT UPLOAD ẢNH TỪ MÁY TÍNH
    # =========================================================================
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
    def build_camera_screen(self):
        workspace = ctk.CTkFrame(self.camera_frame, fg_color="transparent")
        workspace.pack(fill="both", expand=True)

        self.video_container = ctk.CTkFrame(workspace, fg_color="#1e1e1e", corner_radius=12)
        self.video_container.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.cam_label = ctk.CTkLabel(self.video_container, text="MÀN HÌNH SCAN TRỐNG\n(Bật Camera hoặc Tải ảnh từ thiết bị để bắt đầu)")
        self.cam_label.pack(fill="both", expand=True)

        result_panel = ctk.CTkFrame(workspace, width=300, fg_color="#2c3e50")
        result_panel.pack(side="right", fill="y")

        self.res_label_val = ctk.CTkLabel(result_panel, text="Chờ quét...", font=ctk.CTkFont(size=20, weight="bold"), text_color="yellow")
        self.res_label_val.pack(pady=20)

<<<<<<< HEAD
        self.btn_toggle_cam = ctk.CTkButton(result_panel, text="Bật Camera", command=self.toggle_camera, fg_color="#1abc9c")
=======
        self.btn_toggle_cam = ctk.CTkButton(result_panel, text="🎥 Bật Camera", command=self.toggle_camera, fg_color="#1abc9c")
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
        self.btn_toggle_cam.pack(pady=5, fill="x", padx=20)

        self.btn_capture_ai = ctk.CTkButton(result_panel, text="Chụp & Phân Tích", command=self.trigger_ai_detection, state="disabled")
        self.btn_capture_ai.pack(pady=5, fill="x", padx=20)
        
<<<<<<< HEAD
        self.btn_upload_device = ctk.CTkButton(result_panel, text="Tải Ảnh Từ Thiết Bị", command=self.upload_image_from_device, fg_color="#9b59b6", hover_color="#8e44ad")
        self.btn_upload_device.pack(pady=5, fill="x", padx=20)
        
        btn_back = ctk.CTkButton(result_panel, text="Quay lại Dashboard", command=self.show_dashboard, fg_color="#7f8c8d")
=======
        # NÚT MỚI: TẢI ẢNH LÊN TỪ MÁY
        self.btn_upload_ai = ctk.CTkButton(result_panel, text="📁 Tải Ảnh Lên & Phân Tích", command=self.upload_image_file, fg_color="#34495e", hover_color="#2c3e50")
        self.btn_upload_ai.pack(pady=5, fill="x", padx=20)
        
        btn_back = ctk.CTkButton(result_panel, text="📊 Quay lại Dashboard", command=self.show_dashboard, fg_color="#7f8c8d")
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
        btn_back.pack(pady=20, fill="x", padx=20)

    def show_dashboard(self):
        self.stop_camera_stream()
        self.camera_frame.pack_forget()
        self.dashboard_frame.pack(fill="both", expand=True)
        threading.Thread(target=self.load_database_records, daemon=True).start()

    def show_camera(self):
        self.dashboard_frame.pack_forget()
        self.camera_frame.pack(fill="both", expand=True)

    def toggle_camera(self):
        if not self.camera_running:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.camera_running = True
                self.btn_toggle_cam.configure(text="Tắt Camera", fg_color="red")
                self.btn_capture_ai.configure(state="normal")
                self.btn_upload_device.configure(state="disabled")
                self.update_camera_stream()
        else:
            self.stop_camera_stream()

    def update_camera_stream(self):
        if self.camera_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy()
                cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(cv2_img).resize((600, 450))
                tk_img = ImageTk.PhotoImage(image=pil_img)
                self.cam_label.configure(image=tk_img, text="")
                self.cam_label.image = tk_img
            self.after(15, self.update_camera_stream)

    def stop_camera_stream(self):
        self.camera_running = False
        if self.cap: self.cap.release()
        self.cap = None
        self.btn_toggle_cam.configure(text="Bật Camera", fg_color="#1abc9c")
        self.btn_capture_ai.configure(state="disabled")
        self.btn_upload_device.configure(state="normal")

    def trigger_ai_detection(self):
        if self.current_frame is not None:
            self.res_label_val.configure(text="AI đang xử lý...")
            threading.Thread(target=self._run_api_process, args=(self.current_frame,), daemon=True).start()

<<<<<<< HEAD
    def upload_image_from_device(self):
        file_path = filedialog.askopenfilename(
            title="Chọn hình ảnh rác thải",
=======
    # HÀM MỞ HỘP THOẠI CHỌN FILE ẢNH
    def upload_image_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh rác thải cần phân tích",
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if not file_path:
            return

<<<<<<< HEAD
        frame = cv2.imread(file_path)
        if frame is None:
            messagebox.showerror("Lỗi", "Không thể đọc file ảnh này.")
            return

        self.current_frame = frame.copy()
        
        cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(cv2_img).resize((600, 450))
        tk_img = ImageTk.PhotoImage(image=pil_img)
        self.cam_label.configure(image=tk_img, text="")
        self.cam_label.image = tk_img

        self.res_label_val.configure(text="AI đang xử lý...")
        threading.Thread(target=self._run_api_process, args=(self.current_frame,), daemon=True).start()

    def _run_api_process(self, frame):
        try:
            # 1. Chuẩn hóa hình ảnh và gửi sang AI Service (Port 8000) để nhận diện
=======
        uploaded_frame = cv2.imread(file_path)
        if uploaded_frame is None:
            messagebox.showerror("Lỗi", "Không thể đọc tệp tin hình ảnh này.")
            return

        # Dừng luồng stream camera để chuẩn bị hiển thị ảnh vừa upload lên màn hình xem trước
        self.stop_camera_stream()
        
        self.res_label_val.configure(text="AI đang xử lý ảnh tải lên...")
        threading.Thread(target=self._run_api_process, args=(uploaded_frame,), daemon=True).start()

    # ĐÃ CẬP NHẬT: LUỒNG XỬ LÝ VẼ KHUNG (BOUNDING BOX) KHI AI PHẢN HỒI TOẠ ĐỘ
    def _run_api_process(self, frame):
        try:
            # Gửi ảnh thô nguyên bản đi phân tích
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
            anh_sach = resize_image(frame)
            du_lieu_bytes = convert_frame_to_bytes(anh_sach)
            ket_qua = upload_waste_image(du_lieu_bytes)
            
            if isinstance(ket_qua, dict) and ket_qua.get("status") == "success":
                label = ket_qua.get("label", "Không rõ")
                conf = ket_qua.get("confidence", "0.00%")
<<<<<<< HEAD
                
                # Hiển thị ngay kết quả chữ màu xanh lên màn hình camera
                self.res_label_val.configure(text=f"{label}\n{conf}", text_color="green")
                
                # =========================================================================
                # BƯỚC THAY ĐỔI QUAN TRỌNG: Giao diện chủ động ra lệnh cho Backend lưu Database
                # =========================================================================
                payload_db = {
                    "label": label,
                    "confidence": conf
                }
                
                # Gọi Backend (Port 5000) để thêm mới bản ghi vào file history_database.db
                response_save = requests.post("http://127.0.0.1:5000/save-result", json=payload_db, timeout=3)
                
                if response_save.status_code == 200:
                    # Sau khi Backend báo lưu DB thành công, lấy danh sách để lấy tên file ảnh tương ứng
                    response_records = requests.get("http://127.0.0.1:5000/api/records", timeout=2)
                    if response_records.status_code == 200 and len(response_records.json()) > 0:
                        latest_record = response_records.json()[0]
                        img_name = latest_record.get("image_path")
                        
                        # Xác định đường dẫn thư mục lưu ảnh vật lý
                        UI_DIR = os.path.dirname(os.path.abspath(__file__))
                        ROOT_DIR = os.path.dirname(UI_DIR)
                        backend_img_dir = os.path.join(ROOT_DIR, "Backend", "saved_images")
                        
                        if not os.path.exists(backend_img_dir):
                            os.makedirs(backend_img_dir)
                            
                        # Ghi file ảnh vật lý trùng khớp tên trong Database
                        cv2.imwrite(os.path.join(backend_img_dir, img_name), frame)
                        print(f"[HỆ THỐNG] Đã lưu ảnh thành công: {img_name}")
                else:
                    print("[LỖI] Backend từ chối ghi nhận lịch sử dữ liệu.")
            else:
                self.res_label_val.configure(text="Lỗi kết nối AI!", text_color="red")
        except Exception as e:
            print(f"[LỖI HỆ THỐNG NGẦM]: {e}")
=======
                box = ket_qua.get("box", []) # Lấy mảng [x1, y1, x2, y2]
                
                # Copy ra 1 bản để vẽ khung hiển thị và lưu (Không làm hỏng frame gốc)
                frame_with_box = frame.copy()
                
                # Nếu AI tìm thấy vật thể và trả ra tọa độ, dùng OpenCV vẽ trực tiếp lên ảnh
                if box and len(box) == 4:
                    x1, y1, x2, y2 = box
                    # 1. Vẽ hình chữ nhật màu xanh lá cây rực rỡ, độ dày nét vẽ là 3
                    cv2.rectangle(frame_with_box, (x1, y1), (x2, y2), (0, 255, 0), 3)

                # Hiển thị bức ảnh ĐÃ CÓ KHUNG lên màn hình chính cho người dùng xem
                self.res_label_val.configure(text=f"{label}\n{conf}", text_color="red")
                cv2_img = cv2.cvtColor(frame_with_box, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(cv2_img).resize((600, 450))
                tk_img = ImageTk.PhotoImage(image=pil_img)
                self.cam_label.configure(image=tk_img, text="")
                self.cam_label.image = tk_img
                
                # Đồng bộ lưu ảnh ĐÃ VẼ KHUNG vào thư mục Backend/saved_images để phục vụ xem lịch sử
                response = requests.get("http://127.0.0.1:5000/api/records", timeout=2)
                if response.status_code == 200 and len(response.json()) > 0:
                    latest_record = response.json()[0]
                    img_name = latest_record.get("image_path")
                    
                    UI_DIR = os.path.dirname(os.path.abspath(__file__))
                    ROOT_DIR = os.path.dirname(UI_DIR)
                    backend_img_dir = os.path.join(ROOT_DIR, "Backend", "saved_images")
                    
                    # Lưu bức ảnh đã vẽ khung xuống ổ cứng
                    cv2.imwrite(os.path.join(backend_img_dir, img_name), frame_with_box)
            else:
                self.res_label_val.configure(text="Lỗi kết nối AI!", text_color="red")
        except Exception as e:
            print(e)
>>>>>>> 658ec50047192b9ba76b1217abf73b7f84a6e84a
            self.res_label_val.configure(text="Lỗi hệ thống!", text_color="red")

if __name__ == "__main__":
    app = WasteApp()
    app.mainloop()