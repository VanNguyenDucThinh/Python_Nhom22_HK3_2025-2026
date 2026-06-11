import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog  # Bảng hiển thị danh sách lịch sử và hộp thoại
from PIL import Image
import os
import sqlite3
import csv

class DataFrameView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#f8f9fa")
        
        # Cấu hình Layout lưới Grid gốc của hệ thống
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)

        # --- ĐƯỜNG DẪN DATABASE VÀ THƯ MỤC ẢNH CỦA NHÓM 22 ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.normpath(os.path.join(current_dir, "..", "Backend", "history_database.db"))
        self.img_dir = os.path.normpath(os.path.join(current_dir, "..", "Backend", "saved_images"))

        # Biến giữ ảnh hiện tại tránh hiện tượng rác bộ nhớ xóa ảnh ngầm (Garbage Collection)
        self.current_display_image = None

        # --- LOAD ICON CHO NÚT BẤM VÀ THÔNG BÁO TRỐNG ---
        logo_path = os.path.join(current_dir, "logo")
        try:
            self.icon_export = ctk.CTkImage(light_image=Image.open(os.path.join(logo_path, "export_white.png")), size=(18, 18))
            self.icon_delete = ctk.CTkImage(light_image=Image.open(os.path.join(logo_path, "delete_white.png")), size=(18, 18))
            self.img_empty_hist = ctk.CTkImage(light_image=Image.open(os.path.join(logo_path, "empty_history.png")), size=(64, 64))
            self.img_empty_det = ctk.CTkImage(light_image=Image.open(os.path.join(logo_path, "empty_detail.png")), size=(64, 64))
        except Exception:
            self.icon_export = self.icon_delete = self.img_empty_hist = self.img_empty_det = None

        # 1. PHẦN TIÊU ĐỀ GIAO DIỆN
        self.header_section = ctk.CTkFrame(self, fg_color="transparent")
        self.header_section.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(self.header_section, text="Quản Lý Dữ Liệu", font=("Arial", 34, "bold"), text_color="black").pack(anchor="w")
        ctk.CTkLabel(self.header_section, text="Xem lại lịch sử phân tích và thống kê", font=("Arial", 17), text_color="gray").pack(anchor="w")

        # 2. KHUNG ĐỒNG BỘ 4 THẺ THỐNG KÊ MÀU SẮC
        self.top_cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_cards_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 25))
        for i in range(4): 
            self.top_cards_frame.grid_columnconfigure(i, weight=1)

        colors = ["#00a843", "#1b66ff", "#dca100", "#e61224"]
        titles = ["Hữu Cơ", "Vô Cơ", "Tái Chế", "Độc Hại"]
        self.card_labels = {} 

        for i in range(4):
            card = ctk.CTkFrame(self.top_cards_frame, fg_color=colors[i], height=135, corner_radius=12)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            card.pack_propagate(False)
            
            ctk.CTkLabel(card, text=titles[i], font=("Arial", 19, "bold"), text_color="white").pack(anchor="w", padx=20, pady=(15, 2))
            
            lbl_count = ctk.CTkLabel(card, text="0", font=("Arial", 40, "bold"), text_color="white")
            lbl_count.pack(anchor="w", padx=20)
            self.card_labels[titles[i]] = lbl_count 
            
            ctk.CTkLabel(card, text="vật thể phát hiện", font=("Arial", 15), text_color="#ffffff").pack(anchor="w", padx=20)

        # 3. KHUNG LỊCH SỬ PHÂN TÍCH (Bên trái)
        self.history_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="white", border_color="#eaedf0", border_width=1)
        self.history_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        
        self.header_hist = ctk.CTkFrame(self.history_frame, fg_color="transparent", height=70)
        self.header_hist.pack(fill="x", padx=22, pady=(10, 5))
        self.header_hist.pack_propagate(False)
        
        self.lbl_hist_title = ctk.CTkLabel(self.header_hist, text="Lịch Sử Phân Tích (0)", font=("Arial", 22, "bold"), text_color="black")
        self.lbl_hist_title.pack(side="left")
        
        ctk.CTkButton(self.header_hist, text=" Xóa Tất Cả", image=self.icon_delete, compound="left", width=130, height=38, fg_color="#ff4d6d", hover_color="#ff1a43", text_color="white", font=("Arial", 14, "bold"), corner_radius=8, command=self.clear_all_data).pack(side="right", padx=5)
        ctk.CTkButton(self.header_hist, text=" Xuất", image=self.icon_export, compound="left", width=100, height=38, fg_color="#4cc9f0", hover_color="#4361ee", text_color="white", font=("Arial", 14, "bold"), corner_radius=8, command=self.export_to_csv).pack(side="right", padx=5)
        
        ctk.CTkFrame(self.history_frame, height=2, fg_color="#eaedf0").pack(fill="x", padx=22, pady=(5, 10))
        
        self.hist_content_area = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.hist_content_area.pack(fill="both", expand=True)

        self.table_frame = ctk.CTkFrame(self.hist_content_area, fg_color="transparent")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Arial", 13), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="#f0f2f5", foreground="black")
        
        self.tree = ttk.Treeview(self.table_frame, columns=("STT", "Thời Gian", "Loại Rác", "Độ Tin Cậy"), show="headings")
        self.tree.heading("STT", text="STT")
        self.tree.heading("Thời Gian", text="Thời Gian")
        self.tree.heading("Loại Rác", text="Loại Rác")
        self.tree.heading("Độ Tin Cậy", text="Độ Tin Cậy")
        self.tree.column("STT", width=60, anchor="center")
        self.tree.column("Thời Gian", width=220, anchor="center")
        self.tree.column("Loại Rác", width=150, anchor="center")
        self.tree.column("Độ Tin Cậy", width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ràng buộc sự kiện click chọn dòng
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        self.empty_hist_label = ctk.CTkLabel(self.hist_content_area, text=" Không có dữ liệu lịch sử", font=("Arial", 15), image=self.img_empty_hist, compound="top", text_color="gray")

        # 4. KHUNG Ô CHI TIẾT BÊN PHẢI (Giữ nguyên cấu trúc giao diện chuẩn của bạn)
        self.detail_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="white", border_color="#eaedf0", border_width=1)
        self.detail_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 0))
        
        header_det = ctk.CTkFrame(self.detail_frame, fg_color="transparent", height=70)
        header_det.pack(fill="x", padx=22, pady=(10, 5))
        header_det.pack_propagate(False)
        ctk.CTkLabel(header_det, text="Thông Tin Chi Tiết", font=("Arial", 22, "bold"), text_color="black").pack(side="left")
        
        ctk.CTkFrame(self.detail_frame, height=2, fg_color="#eaedf0").pack(fill="x", padx=22, pady=(5, 15))
        
        self.det_content_area = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        self.det_content_area.pack(fill="both", expand=True)

        self.empty_det_label = ctk.CTkLabel(self.det_content_area, text="Chọn một dòng để xem chi tiết", font=("Arial", 15), image=self.img_empty_det, compound="top", text_color="gray")
        self.empty_det_label.pack(expand=True)

        # Container chứa thông tin chi tiết dạng text
        self.info_container = ctk.CTkFrame(self.det_content_area, fg_color="transparent")
        
        self.lbl_det_id = self._create_detail_row(self.info_container, "Mã định danh:")
        self.lbl_det_time = self._create_detail_row(self.info_container, "Thời gian quét:")
        self.lbl_det_label = self._create_detail_row(self.info_container, "Kết quả phân loại:")
        self.lbl_det_conf = self._create_detail_row(self.info_container, "Độ tin cậy của AI:")

        # Ô BOX CHỨA ẢNH CHI TIẾT ĐƯỢC TÍCH HỢP THÊM VÀO PHÍA DƯỚI KHUNG CHI TIẾT
        self.lbl_detail_image = ctk.CTkLabel(
            self.info_container, 
            text="Hình ảnh minh chứng thực tế", 
            fg_color="#f8f9fa", 
            corner_radius=10,
            width=280,
            height=210,
            font=("Arial", 13)
        )
        self.lbl_detail_image.pack(pady=(20, 10), padx=20, fill="both", expand=True)

        # Nạp dữ liệu tự động lần đầu
        self._load_data_from_db()

    def _create_detail_row(self, parent, label_text):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(row, text=label_text, font=("Arial", 14, "bold"), text_color="#555555", width=130, anchor="w").pack(side="left")
        val_lbl = ctk.CTkLabel(row, text="", font=("Arial", 14), text_color="black", anchor="w")
        val_lbl.pack(side="left", fill="x", expand=True)
        return val_lbl

    def _on_tree_select(self, event):
        """Xử lý sự kiện click chọn một dòng trong bảng hiển thị lịch sử"""
        selected = self.tree.selection()
        if not selected:
            return
            
        # 1. Ẩn nhãn thông báo trống, kích hoạt khung hiển thị chi tiết
        self.empty_det_label.pack_forget()
        self.info_container.pack(fill="both", expand=True)
        
        # 2. Trích xuất mảng dữ liệu của dòng vừa bấm
        row_data = self.tree.item(selected[0], "values")
        if not row_data:
            return
            
        record_id = str(row_data[0]).replace("#", "").strip()
        timestamp = row_data[1]
        label_name = row_data[2]
        confidence = row_data[3]
        
        # 3. Kết xuất text ra các nhãn tương ứng
        self.lbl_det_id.configure(text=f"#{record_id}")
        self.lbl_det_time.configure(text=timestamp)
        self.lbl_det_label.configure(text=label_name)
        self.lbl_det_conf.configure(text=confidence)
        
        # 4. Tìm kiếm đường dẫn liên kết ảnh từ cột thứ 5 (Ẩn ngầm) hoặc fallback theo ID
        image_name = ""
        if len(row_data) > 4 and row_data[4]:
            image_name = row_data[4]
        else:
            image_name = f"history_{record_id}.jpg"
            
        # Kiểm tra xem dữ liệu trong db là đường dẫn tuyệt đối hay chỉ là tên file đơn thuần
        if os.path.isabs(image_name):
            target_image_path = image_name
        else:
            target_image_path = os.path.join(self.img_dir, image_name)
        
        # 5. Đọc file ảnh vật lý lên giao diện người dùng
        if os.path.exists(target_image_path):
            try:
                pil_img = Image.open(target_image_path)
                # Đổi kích thước thành 280x210 phù hợp khít khung Detail của nhóm
                self.current_display_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(280, 210))
                self.lbl_detail_image.configure(image=self.current_display_image, text="")
            except Exception as e:
                print(f"[ERR] Không đọc được file ảnh {image_name}: {e}")
                self.lbl_detail_image.configure(image=None, text="⚠️ Tệp hình ảnh bị lỗi")
        else:
            self.lbl_detail_image.configure(image=None, text="❌ Không tìm thấy file ảnh")

    def _load_data_from_db(self):
        """Truy vấn dữ liệu từ SQLite, cập nhật số lượng lên 4 thẻ màu và làm mới bảng"""
        if not os.path.exists(self.db_path):
            self.table_frame.pack_forget()
            self.empty_hist_label.pack(expand=True)
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Đếm tổng số lượng rác của từng nhóm gán vào 4 thẻ màu
            cursor.execute("SELECT label, COUNT(*) FROM WasteHistory GROUP BY label")
            counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            self.card_labels["Hữu Cơ"].configure(text=str(counts.get("Rác hữu cơ", 0)))
            self.card_labels["Vô Cơ"].configure(text=str(counts.get("Rác vô cơ", 0)))
            self.card_labels["Tái Chế"].configure(text=str(counts.get("Rác tái chế", 0)))
            self.card_labels["Độc Hại"].configure(text=str(counts.get("Rác độc hại", 0)))
            
            # Cơ chế kiểm tra an toàn: Lấy 5 cột nếu có cột liên kết ảnh, tự động fallback 4 cột cũ nếu chưa đổi cấu trúc DB
            try:
                cursor.execute("SELECT id, timestamp, label, confidence, image_path FROM WasteHistory ORDER BY id DESC")
                rows = cursor.fetchall()
                has_img_col = True
            except sqlite3.OperationalError:
                cursor.execute("SELECT id, timestamp, label, confidence FROM WasteHistory ORDER BY id DESC")
                rows = cursor.fetchall()
                has_img_col = False
            
            self.lbl_hist_title.configure(text=f"Lịch Sử Phân Tích ({len(rows)})")
            
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            if not rows:
                self.table_frame.pack_forget()
                self.empty_hist_label.pack(expand=True)
                self.info_container.pack_forget()
                self.empty_det_label.pack(expand=True)
            else:
                self.empty_hist_label.pack_forget()
                self.table_frame.pack(fill="both", expand=True, padx=22, pady=(0, 20))
                
                for r in rows:
                    # Mẹo Tkinter: Đút giá trị liên kết ảnh vào cuối mảng values (ẩn ngầm không hiện lên cột bảng)
                    img_val = r[4] if has_img_col else f"history_{r[0]}.jpg"
                    self.tree.insert("", "end", values=(f"#{r[0]}", r[1], r[2], r[3], img_val))
            conn.close()
        except Exception as e:
            print(f"[DATABASE ERROR]: {e}")

    def clear_all_data(self):
        if not os.path.exists(self.db_path):
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa toàn bộ lịch sử phân loại không?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM WasteHistory")
                conn.commit()
                conn.close()
                
                # Làm sạch toàn bộ ảnh lưu vật lý
                if os.path.exists(self.img_dir):
                    for f in os.listdir(self.img_dir):
                        if f.endswith(".jpg") or f.endswith(".png"):
                            try:
                                os.remove(os.path.join(self.img_dir, f))
                            except Exception:
                                pass
                            
                self._load_data_from_db()
                messagebox.showinfo("Thành công", "Đã xóa sạch dữ liệu lịch sử thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa dữ liệu: {e}")

    def export_to_csv(self):
        if not os.path.exists(self.db_path):
            messagebox.showwarning("Thông báo", "Không có dữ liệu để xuất file!")
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, label, confidence FROM WasteHistory ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                messagebox.showwarning("Thông báo", "Danh sách lịch sử rỗng!")
                return
                
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Chọn nơi lưu file báo cáo",
                initialfile="Bao_Cao_Lich_Su_Phan_Loai_Rac.csv"
            )
            if not file_path: 
                return
                
            with open(file_path, mode="w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["STT", "Thời Gian Quét", "Loại Rác Phát Hiện", "Độ Tin Cậy"])
                for r in rows:
                    try:
                        conf_val = float(r[3])
                        conf_str = f"{conf_val * 100:.1f}%" if conf_val <= 1.0 else f"{r[3]}"
                    except ValueError:
                        conf_str = str(r[3])
                    writer.writerow([r[0], r[1], r[2], conf_str])
                    
            messagebox.showinfo("Thành công", "Đã xuất file báo cáo lịch sử thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xuất file: {e}")