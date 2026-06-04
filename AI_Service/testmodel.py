import os
import cv2
from ultralytics import YOLO

# 1. Nạp model
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(CURRENT_DIR, "best.pt")
if not os.path.exists(model_path):
    print(f"[LỖI]: Không tìm thấy file {model_path}")
    exit()

print("--- ĐANG KIỂM TRA FILE MODEL ---")
model = YOLO(model_path)

# In ra kiểu bài toán của mô hình (Xem có phải bài toán Phân loại - Classify không)
print(f"-> Kiểu tác vụ của Model (Task): {model.task}")
print(f"-> Danh sách các nhãn đã học (Names): {model.names}")

# 2. Tạo một ảnh giả lập (ma trận đen) kích thước 224x224 để test dự đoán
print("\n--- CHẠY THỬ DỰ ĐOÁN NGẦM ---")
dummy_frame = (255 * (0.5 * (1 + 0))).view(dtype='uint8') # Tạo khung ảnh trống nhanh
dummy_frame =  cv2.resize(cv2.imread(r"images\.keep") if os.path.exists(r"images\.keep") else None or  (255*bytes([0]*224*224*3)), (224, 224)) # hoặc dùng ảnh bất kỳ

# Bạn có thể thay bằng đường dẫn 1 ảnh rác thật bất kỳ để test trực quan:
# dummy_frame = cv2.imread("duong_dan_anh_rac.jpg") 

try:
    results = model(dummy_frame)
    print("[OK] Model chạy dự đoán (Inference) mượt mà!")
    
    # Kiểm tra cấu trúc đầu ra xem có thuộc tính .probs không
    probs = results[0].probs
    print(f"-> Giá trị thuộc tính .probs: {probs}")
    
    if probs is None:
        print("\n[CẢNH BÁO NGUY HIỂM]: Thuộc tính .probs trả về None!")
        print("=> Nguyên nhân: Bạn đang sài model Object Detection (Phát hiện vật thể) hoặc Segment.")
        print("=> Code hiện tại của bạn dùng lệnh 'probs.top1' nên khi probs=None sẽ lập tức crash 500!")
    else:
        print(f"-> Top 1 Class Index: {probs.top1}")
        print(f"-> Top 1 Confidence: {probs.top1conf}")
        print("[THÀNH CÔNG] File best.pt hoàn hảo, không lỗi cấu trúc.")

except Exception as e:
    print(f"\n[PHÁT HIỆN LỖI CRASH]: {e}")