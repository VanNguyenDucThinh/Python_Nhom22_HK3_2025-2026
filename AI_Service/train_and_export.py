# train_and_export.py
import os
from ultralytics import YOLO

def main():
    print("=" * 60)
    print("--- QUY TRÌNH HUẤN LUYỆN AI PHÁT HIỆN VẬT THỂ (OBJECT DETECTION) ---")
    print("=" * 60)

    # 1. Bài toán Detect bắt buộc phải dùng file cấu hình data.yaml
    # Bạn cần tạo 1 file tên là data.yaml nằm trong thư mục dataset để khai báo đường dẫn và các class rác
    yaml_path = os.path.abspath("AI_Service/dataset/data.yaml")
    
    if not os.path.exists(yaml_path):
        print(f"[LỖI]: Không tìm thấy file cấu hình tại: {yaml_path}")
        print("👉 Hướng dẫn: Đối với bài toán Detect, bạn phải tạo file 'data.yaml' chứa cấu hình đường dẫn và tên class.")
        return

    print("[BƯỚC 1/3] Đang nạp mô hình YOLOv8 Nano Detect siêu nhẹ...")
    # ĐÃ SỬA: Bỏ đuôi '-cls.pt', đổi sang dùng mô hình gốc yolov8n.pt để nhận diện vẽ khung bao
    model = YOLO("yolov8n.pt") 

    print("[BƯỚC 2/3] Bắt đầu quá trình huấn luyện (Training Object Detection)...")
    # Huấn luyện với cấu hình yaml của bạn trong 5 vòng (epochs) để test trước
    results = model.train(
        data=yaml_path,     # ĐÃ SỬA: Truyền file data.yaml thay vì truyền đường dẫn thư mục dataset_path
        epochs=5, 
        imgsz=640,          # ĐÃ SỬA: Kích thước ảnh chuẩn của bài toán Detect là 640 (thay vì 224 của classify)
        workers=0           # Giúp tránh lỗi xung đột luồng dữ liệu trên Windows
    )

    print("\n" + "=" * 60)
    print("[BƯỚC 3/3] Huấn luyện xong! Đang tiến hành xuất file Model...")
    
    # 3. Xuất model sang định dạng ONNX nếu bạn cần nhúng vào phần mềm khác
    exported_path = model.export(format="onnx")
    
    print(f"\n[XUẤT FILE THÀNH CÔNG]: File mô hình ONNX đạt chuẩn tại:\n👉 {exported_path}")
    print("👉 File 'best.pt' chuẩn Detect của bạn sẽ nằm tại: AI_Service/runs/detect/train/weights/best.pt")
    print("=" * 60)

if __name__ == "__main__":
    main()