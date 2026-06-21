import os
import cv2
import threading
import time
import sys
import numpy as np
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests

current_file_path = os.path.abspath(__file__)          # Duong dan den camera_view.py
view_dir = os.path.dirname(current_file_path)         # Thu muc view
PROJECT_ROOT = os.path.dirname(view_dir)              # Thu muc goc do an

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from CameraService import image_processor
except ImportError as e:
    print(f"[LOI NAP MODULE TRONG CAMERA_VIEW]: {e}")
    image_processor = None

class CameraView(ctk.CTkFrame):
    def __init__(self, master, cam_id=0, switch_view_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.cam_id = int(cam_id) if str(cam_id).isdigit() else 0
        self.switch_view_callback = switch_view_callback
        self.cap = None
        self.is_running = False
        self.is_camera_active = True 
        
        self._last_frame = None
        self._current_tk_image = None
        
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

        # --- LOAD ICON TỪ FOLDER ASSETS ---
        try:
            img_return = ctk.CTkImage(Image.open(os.path.join(assets_dir, "return.png")), size=(20, 20))
            self.img_camera = ctk.CTkImage(Image.open(os.path.join(assets_dir, "camera.png")), size=(20, 20))
            self.img_upload = ctk.CTkImage(Image.open(os.path.join(assets_dir, "upload.png")), size=(20, 20))
        except FileNotFoundError:
            img_return = self.img_camera = self.img_upload = None

        self.btn_back = ctk.CTkButton(
            self.top_bar, text=" Quay lại chọn camera", image=img_return, compound="left",
            fg_color="transparent", text_color="#495057", hover_color="#e9ecef", 
            anchor="w", command=self._go_back
        )
        self.btn_back.pack(side="left")

        self.video_container = ctk.CTkFrame(self.cam_frame, fg_color="black", corner_radius=10)
        self.video_container.pack(expand=True, fill="both", padx=10, pady=(10, 0))
        self.video_container.pack_propagate(False)

        self.video_label = ctk.CTkLabel(self.video_container, text="Đang tải Camera...", fg_color="black")
        self.video_label.pack(expand=True, fill="both")

        self.btn_frame = ctk.CTkFrame(self.cam_frame, fg_color="transparent")
        self.btn_frame.pack(pady=15)

        # --- GẮN ICON VÀO NÚT BẤM ---
        self.btn_capture = ctk.CTkButton(
            self.btn_frame, text=" Chụp Ảnh", image=self.img_camera, compound="left", command=self._handle_capture_btn, 
            fg_color="#00b050", hover_color="#008f40", height=40, width=150
        )
        self.btn_capture.pack(side="left", padx=10)

        self.btn_upload = ctk.CTkButton(
            self.btn_frame, text=" Tải Ảnh Lên", image=self.img_upload, compound="left", command=self._upload_image_from_file,
            fg_color="#0d6efd", hover_color="#0b5ed7", height=40, width=150
        )
        self.btn_upload.pack(side="left", padx=10)

        # --- PANEL PHẢI: KẾT QUẢ & HƯỚNG DẪN ---
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.result_frame = ctk.CTkFrame(self.right_frame, fg_color="white", corner_radius=10)
        self.result_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.result_frame, text="Kết Quả Phân Tích", font=ctk.CTkFont(size=16, weight="bold"), text_color="#102a43").pack(pady=15, anchor="w", padx=20)
        self.result_label = ctk.CTkLabel(self.result_frame, text="[📷]\nChụp hoặc tải ảnh lên để phân tích", text_color="#829ab1", justify="center")
        self.result_label.pack(pady=(20, 50))
        # --- Thêm mới nút tải lại ---
        self.btn_retry = ctk.CTkButton(
            self.result_frame,
            text="Thử Lại",
            command=self._retry_analysis,
            fg_color="#6c757d", hover_color="#5a6268", 
            height=30, width=120, corner_radius=8
        )
        # -----------------------------------

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
        self.cap = cv2.VideoCapture(self.cam_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.cap.isOpened():
            self.video_label.configure(text="Lỗi: Không kết nối được Camera!", text_color="red")
            return
        
        self.is_running = True
        self.is_camera_active = True
        threading.Thread(target=self._camera_reader_thread, daemon=True).start()
        self._update_frame()

    def _camera_reader_thread(self):
        for _ in range(5):
            if self.cap.isOpened():
                self.cap.read()
                time.sleep(0.05)

        while self.is_running and self.cap.isOpened():
            if self.is_camera_active:
                ret, frame = self.cap.read()
                if ret:
                    self._last_frame = cv2.flip(frame, 1)
            time.sleep(0.01)

    def _update_frame(self):
        if not self.is_running:
            return

        if self._last_frame is not None and self.is_camera_active:
            self._render_image_to_screen(self._last_frame)

        self.after(30, self._update_frame)

    def _render_image_to_screen(self, frame):
        target_width = self.video_container.winfo_width()
        target_height = self.video_container.winfo_height()

        if target_width > 10 and target_height > 10:
            resized_frame = cv2.resize(frame, (target_width, target_height))
            cv2_image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv2_image)
            
            self._current_tk_image = ImageTk.PhotoImage(image=pil_image)
            self.video_label.configure(image=self._current_tk_image, text="")

    def _handle_capture_btn(self):
        if self.is_camera_active:
            if self._last_frame is None:
                self.result_label.configure(text="Không có khung ảnh để chụp.", text_color="red")
                return
            
            self.result_label.configure(text="AI đang xử lý...", text_color="#0d6efd")
            # GỌI LUỒNG _run_api_process GIỐNG HỆT NHƯ TEMPINTERFACE.PY CŨ
            threading.Thread(target=self._run_api_process, args=(self._last_frame.copy(),), daemon=True).start()
        else:
            self.is_camera_active = True
            self.btn_capture.configure(text=" Chụp Ảnh", fg_color="#00b050", hover_color="#008f40", text_color="white")
            self.result_label.configure(text="[📷]\nCamera đã được bật lại", text_color="#829ab1")

    def _upload_image_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh rác thải",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        
        if file_path:
            self.is_camera_active = False
            self.btn_capture.configure(text=" Bật lại Camera", fg_color="#ffc107", hover_color="#e0a800", text_color="black")
            
            try:
                stream = open(file_path, "rb")
                bytes_array = bytearray(stream.read())
                numpy_array = np.asarray(bytes_array, dtype=np.uint8)
                uploaded_frame = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
                
                if uploaded_frame is not None:
                    self._last_frame = uploaded_frame
                    self._render_image_to_screen(uploaded_frame)
                    
                    self.result_label.configure(text="AI đang xử lý ảnh tải lên...", text_color="#0d6efd")
                    # GỌI LUỒNG _run_api_process GIỐNG HỆT NHƯ TEMPINTERFACE.PY CŨ
                    threading.Thread(target=self._run_api_process, args=(uploaded_frame.copy(),), daemon=True).start()
                else:
                    self.result_label.configure(text="Lỗi: File ảnh không hợp lệ!", text_color="red")
            except Exception as e:
                self.result_label.configure(text=f"Lỗi hệ thống: {e}", text_color="red")

    # =========================================================================
    # ĐÃ PHỤC HỒI: HÀM _run_api_process GIỮ NGUYÊN LOGIC CỦA TEMPINTERFACE.PY
    # =========================================================================
    def _run_api_process(self, frame):
        try:
            # 1. Tiền xử lý ảnh
            if image_processor:
                anh_sach = image_processor.resize_image(frame)
                du_lieu_bytes = image_processor.convert_frame_to_bytes(anh_sach)
            else:
                success, encoded_image = cv2.imencode('.jpg', frame)
                du_lieu_bytes = encoded_image.tobytes()

            # 2. Gửi ảnh lên AI Service (Sử dụng URL trực tiếp để tránh lỗi config)
            files = {'image': ('waste.jpg', du_lieu_bytes, 'image/jpeg')}
            response = requests.post("http://127.0.0.1:8000/predict", files=files, timeout=10)
            
            if response.status_code == 200:
                ket_qua = response.json()
                
                if ket_qua.get("status") == "success":
                    label = ket_qua.get("label", "Không rõ")
                    conf = ket_qua.get("confidence", "0.00%")
                    box = ket_qua.get("box", [])
                    
                    # Copy ra 1 bản để vẽ khung hiển thị và lưu
                    frame_with_box = frame.copy()
                    
                    if label != "Không nhận diện được":
                        # Vẽ hình chữ nhật màu xanh lá cây rực rỡ nếu có tọa độ
                        if box and len(box) == 4:
                            x1, y1, x2, y2 = box
                            cv2.rectangle(frame_with_box, (x1, y1), (x2, y2), (0, 255, 0), 3)

                        # Hiển thị kết quả lên giao diện
                        self.result_label.configure(text=f"📦 {label}\nTin cậy: {conf}", text_color="#00b050")
                        
                        # Giao diện chủ động ra lệnh cho Backend lưu Database
                        payload_db = {"label": label, "confidence": conf}
                        response_save = requests.post("http://127.0.0.1:5000/save-result", json=payload_db, timeout=3)
                        
                        if response_save.status_code == 200:
                            # Lấy tên file ảnh từ Backend để lưu
                            response_records = requests.get("http://127.0.0.1:5000/api/records", timeout=2)
                            if response_records.status_code == 200 and len(response_records.json()) > 0:
                                latest_record = response_records.json()[0]
                                img_name = latest_record.get("image_path")
                                
                                backend_img_dir = os.path.join(PROJECT_ROOT, "Backend", "saved_images")
                                if not os.path.exists(backend_img_dir):
                                    os.makedirs(backend_img_dir)
                                    
                                # Ghi file ảnh vật lý trùng khớp tên trong Database
                                cv2.imwrite(os.path.join(backend_img_dir, img_name), frame_with_box)
                                print(f"[HỆ THỐNG] Đã lưu ảnh thành công: {img_name}")
                    else:
                        self.result_label.configure(text=f"❌ {label}", text_color="red")
                    
                    # Hiển thị bức ảnh ĐÃ CÓ KHUNG lên màn hình chính
                    self._render_image_to_screen(frame_with_box)
                    
                else:
                    self.result_label.configure(text=f"Lỗi AI: {ket_qua.get('message')}", text_color="red")
            else:
                self.result_label.configure(text="Lỗi kết nối AI!", text_color="red")
                
        except Exception as e:
            print(f"[LỖI HỆ THỐNG NGẦM]: {e}")
            self.result_label.configure(text="Lỗi hệ thống!", text_color="red")
        finally:
            self.btn_retry.pack(pady=(0, 15))

    def _retry_analysis(self):
        self.btn_retry.pack_forget()

        if self._last_frame is None:
            self.result_label.configure(text="Chưa có ảnh nào để thử lại!", text_color="red")
            return
            
        self.result_label.configure(text="AI đang xử lý lại...", text_color="#0d6efd")
        
        threading.Thread(target=self._run_api_process, args=(self._last_frame.copy(),), daemon=True).start()
        
    def _go_back(self):
        if self.switch_view_callback:
            self.switch_view_callback(target_view="select_cam")

    def destroy(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        super().destroy()