import os
from ultralytics import YOLO

def main():
    print("=" * 60)
    print("--- QUY TRÌNH HUẤN LUYỆN AI PHÂN LOẠI RÁC BẰNG YOLO ---")
    print("=" * 60)

    # 1. Đường dẫn tới thư mục dataset
    dataset_path = os.path.abspath("AI_Service/dataset")
    
    if not os.path.exists(dataset_path):
        print(f"[LỖI]: Không tìm thấy thư mục tại: {dataset_path}")
        print("👉 Hướng dẫn: Bạn phải tạo folder 'dataset' nằm trong 'AI_Service'.")
        return

    print("[BƯỚC 1/3] Đang nạp mô hình YOLOv8 Nano siêu nhẹ...")
    # Sử dụng mô hình YOLOv8-classify phiên bản Nano để máy chạy cực nhanh
    model = YOLO("yolov8n-cls.pt") 

    print("[BƯỚC 2/3] Bắt đầu quá trình huấn luyện (Training)...")
    # Huấn luyện với dataset của bạn trong 5 vòng (epochs) để test trước
    results = model.train(
        data=dataset_path, 
        epochs=5, 
        imgsz=224, 
        workers=0  # Để workers=0 giúp tránh lỗi xung đột luồng trên Windows
    )

    print("\n" + "=" * 60)
    print("[BƯỚC 3/3] Huấn luyện xong! Đang tiến hành xuất file Model...")
    
    # 3. Xuất model sang định dạng ONNX để nhúng vào phần mềm chính
    exported_path = model.export(format="onnx")
    
    print(f"\n[XUẤT FILE THÀNH CÔNG]: File mô hình đạt chuẩn tại:\n👉 {exported_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()