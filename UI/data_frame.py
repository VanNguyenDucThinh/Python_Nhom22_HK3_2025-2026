import customtkinter as ctk
from tkinter import ttk  # Dùng để vẽ bảng hiển thị danh sách lịch sử
from PIL import Image
import os
import sqlite3

class DataFrameView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#f8f9fa")
        
        # Cấu hình Layout lưới Grid
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)

        # --- ĐƯỜNG DẪN DATABASE CHÍNH XÁC CỦA NHÓM 22 ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.normpath(os.path.join(current_dir, "..", "Backend", "history_database.db"))

        # --- LOAD ICON CHO NÚT BẤM VÀ THÔNG BÁO TRỐNG ---
        logo_path = os.path.join(current_dir, "logo")
        try:
            self.icon_export = ctk.CTkImage(light_image=Image.open(os.path.join(logo_path, "export_white.png")), size=(18, 18))
            self.icon_delete = ctk.CTkImage(light_image=Image.open(os.path.join(logo_path, "delete_white.png")), size=(18, 18))
            self.img_empty_hist = ctk.CTkImage(light_image=Image.open(os.path.join(logo_path, "empty_history.png")), size=(64, 64))
            self.img_empty_det = ctk.CTkImage(light_image=Image.open(os.path.join(logo_path, "empty_detail.png")), size=(64, 64))
        except Exception as e:
            self.icon_export = self.icon_delete = self.img_empty_hist = self.img_empty_det = None

        # 1. PHẦN TIÊU ĐỀ
        self.header_section = ctk.CTkFrame(self, fg_color="transparent")
        self.header_section.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(self.header_section, text="Quản Lý Dữ Liệu", font=("Arial", 34, "bold"), text_color="black").pack(anchor="w")
        ctk.CTkLabel(self.header_section, text="Xem lại lịch sử phân tích và thống kê", font=("Arial", 17), text_color="gray").pack(anchor="w")

        # 2. KHUNG 4 THẺ THỐNG KÊ
        self.top_cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_cards_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 25))
        for i in range(4): self.top_cards_frame.grid_columnconfigure(i, weight=1)

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
        
        # Nút bấm đã được tối ưu màu sắc tương phản cao, rõ chữ và rõ icon
        ctk.CTkButton(self.header_hist, text=" Xóa Tất Cả", image=self.icon_delete, compound="left", width=130, height=38, fg_color="#ff4d6d", hover_color="#ff1a43", text_color="white", font=("Arial", 14, "bold"), corner_radius=8, command=self.clear_all_data).pack(side="right", padx=5)
        ctk.CTkButton(self.header_hist, text=" Xuất", image=self.icon_export, compound="left", width=100, height=38, fg_color="#4cc9f0", hover_color="#4361ee", text_color="white", font=("Arial", 14, "bold"), corner_radius=8,command=self.export_to_csv).pack(side="right", padx=5)
        
        ctk.CTkFrame(self.history_frame, height=2, fg_color="#eaedf0").pack(fill="x", padx=22, pady=(5, 10))
        
        # VÙNG CHỨA NỘI DUNG LỊCH SỬ ĐỘNG
        self.hist_content_area = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.hist_content_area.pack(fill="both", expand=True)

        # Cấu hình sẵn khung chứa bảng dữ liệu
        self.table_frame = ctk.CTkFrame(self.hist_content_area, fg_color="transparent")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Arial", 13), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="#f0f2f5", foreground="black")
        
        # Đã sửa lỗi khai báo chính xác self.table_frame
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
        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

        # 4. KHUNG CHI TIẾT (Bên phải)
        self.detail_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="white", border_color="#eaedf0", border_width=1)
        self.detail_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 0))
        
        self.header_det = ctk.CTkFrame(self.detail_frame, fg_color="transparent", height=70)
        self.header_det.pack(fill="x", padx=22, pady=(10, 5))
        self.header_det.pack_propagate(False)
        ctk.CTkLabel(self.header_det, text="Chi Tiết", font=("Arial", 22, "bold"), text_color="black").pack(side="left")
        ctk.CTkFrame(self.detail_frame, height=2, fg_color="#eaedf0").pack(fill="x", padx=22, pady=(5, 10))
        
        self.detail_content_area = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        self.detail_content_area.pack(fill="both", expand=True)
        
        self.show_empty_detail_state()

        # TỰ ĐỘNG KIỂM TRA DATABASE KHI MỞ APP
        self.load_data_from_database()

    def show_empty_history_state(self):
        self.table_frame.pack_forget() 
        for widget in self.hist_content_area.winfo_children():
            if widget != self.table_frame:
                widget.destroy()
                
        empty_hist_center = ctk.CTkFrame(self.hist_content_area, fg_color="transparent")
        empty_hist_center.pack(expand=True)
        if self.img_empty_hist:
            ctk.CTkLabel(empty_hist_center, text="", image=self.img_empty_hist).pack(pady=(0, 15))
        ctk.CTkLabel(empty_hist_center, text="Chưa có dữ liệu phân tích nào", text_color="#a0a5aa", font=("Arial", 17, "bold")).pack()

    def show_empty_detail_state(self):
        for widget in self.detail_content_area.winfo_children():
            widget.destroy()
        empty_det_center = ctk.CTkFrame(self.detail_content_area, fg_color="transparent")
        empty_det_center.pack(expand=True)
        if self.img_empty_det:
            ctk.CTkLabel(empty_det_center, text="", image=self.img_empty_det).pack(pady=(0, 15))
        ctk.CTkLabel(empty_det_center, text="Chọn một mục để xem chi tiết", text_color="#a0a5aa", font=("Arial", 17, "bold")).pack()

    # ==========================================
    # 🔄 ĐỌC DỮ LIỆU TỪ BẢNG waste_history
    # ==========================================
    def load_data_from_database(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not os.path.exists(self.db_path):
            self.show_empty_history_state()
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Đọc dữ liệu chuẩn theo cấu hình cột thật của nhóm
            cursor.execute("SELECT timestamp, label, confidence FROM waste_history ORDER BY id DESC")
            rows = cursor.fetchall()
            
            if len(rows) == 0:
                self.show_empty_history_state()
            else:
                for widget in self.hist_content_area.winfo_children():
                    if widget != self.table_frame:
                        widget.destroy()
                
                self.table_frame.pack(fill="both", expand=True, padx=22, pady=10)
                
                for stt, row in enumerate(rows, start=1):
                    timestamp, label, confidence = row
                    
                    # Chuẩn hóa hiển thị số phần trăm độ tin cậy (.1f là làm tròn 1 chữ số thập phân)
                    try:
                        conf_val = float(confidence)
                        if conf_val <= 1.0:
                            conf_str = f"{conf_val * 100:.1f}%"
                        else:
                            conf_str = f"{conf_val:.1f}%"
                    except ValueError:
                        conf_str = str(confidence)
                        
                    self.tree.insert("", "end", values=(stt, timestamp, label, conf_str))
            
            self.lbl_hist_title.configure(text=f"Lịch Sử Phân Tích ({len(rows)})")
            
            # Đếm tổng số lượng cho 4 thẻ màu theo đúng từ khóa tiếng Việt nhóm đang lưu trong db
            db_keywords = ["Rác hữu cơ", "Rác vô cơ", "Rác tái chế", "Rác độc hại"]
            ui_titles = ["Hữu Cơ", "Vô Cơ", "Tái Chế", "Độc Hại"]
            
            for keyword, ui_title in zip(db_keywords, ui_titles):
                cursor.execute("SELECT COUNT(*) FROM waste_history WHERE label = ?", (keyword,))
                count = cursor.fetchone()[0]
                self.card_labels[ui_title].configure(text=str(count))
                
            conn.close()
        except Exception as e:
            print(f"Lỗi truy vấn cơ sở dữ liệu thật: {e}")
            self.show_empty_history_state()

    # Hiển thị thông tin chi tiết thật của dòng được click sang cột phải
    def on_row_selected(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
            
        item_data = self.tree.item(selected_item[0])["values"]
        _, timestamp, label, conf_str = item_data
        
        for widget in self.detail_content_area.winfo_children():
            widget.destroy()
            
        info_box = ctk.CTkFrame(self.detail_content_area, fg_color="transparent")
        info_box.pack(fill="both", expand=True, padx=25, pady=20)
        
        ctk.CTkLabel(info_box, text="THÔNG TIN PHÂN TÍCH", font=("Arial", 18, "bold"), text_color="#00a843").pack(anchor="w", pady=(0, 15))
        ctk.CTkLabel(info_box, text=f"• Thời gian quét:", font=("Arial", 15, "bold"), text_color="black").pack(anchor="w", pady=2)
        ctk.CTkLabel(info_box, text=f"  {timestamp}", font=("Arial", 15), text_color="gray").pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(info_box, text=f"• Kết quả phân loại:", font=("Arial", 15, "bold"), text_color="black").pack(anchor="w", pady=2)
        ctk.CTkLabel(info_box, text=f"  {label}", font=("Arial", 16, "bold"), text_color="#1b66ff").pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(info_box, text=f"• Độ tin cậy thuật toán:", font=("Arial", 15, "bold"), text_color="black").pack(anchor="w", pady=2)
        ctk.CTkLabel(info_box, text=f"  {conf_str}", font=("Arial", 15), text_color="gray").pack(anchor="w")

    # Xử lý xóa toàn bộ dữ liệu trong bảng của nhóm
    def clear_all_data(self):
        if not os.path.exists(self.db_path): return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM waste_history")
            conn.commit()
            conn.close()
            self.load_data_from_database()
            self.show_empty_detail_state()
        except Exception as e:
            print(f"Lỗi khi xóa bảng dữ liệu: {e}")
    
    def export_to_csv(self):
        if not os.path.exists(self.db_path): return
        
        import csv
        from tkinter import filedialog, messagebox
        
        try:
            # 1. Đọc toàn bộ dữ liệu từ database của nhóm ra
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, label, confidence FROM waste_history ORDER BY id ASC")
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) == 0:
                messagebox.showwarning("Thông báo", "Hiện tại chưa có dữ liệu nào để xuất file!")
                return
                
            # 2. Hiện hộp thoại hỏi người dùng muốn lưu file Excel/CSV ở thư mục nào trong máy
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Chọn nơi lưu file báo cáo",
                initialfile="Bao_Cao_Lich_Su_Phan_Loai_Rac.csv"
            )
            
            if not file_path: return # Người dùng bấm Cancel, không lưu nữa
            
            # 3. Tiến hành ghi dữ liệu vào file (Cấu hình mã hóa utf-8-sig để Excel đọc được tiếng Việt)
            with open(file_path, mode="w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file)
                # Ghi dòng tiêu đề cột
                writer.writerow(["STT", "Thời Gian Quét", "Loại Rác Phát Hiện", "Độ Tin Cậy"])
                # Ghi toàn bộ các dòng dữ liệu
                for row in rows:
                    # Chuẩn hóa hiển thị % giống trên bảng
                    try:
                        conf_val = float(row[3])
                        conf_str = f"{conf_val * 100:.1f}%" if conf_val <= 1.0 else f"{conf_val:.1f}%"
                    except ValueError:
                        conf_str = str(row[3])
                        
                    writer.writerow([row[0], row[1], row[2], conf_str])
                    
            messagebox.showinfo("Thành công", "Đã xuất file báo cáo lịch sử thành công!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")