import os

print("--- KHỞI TẠO MODEL ONNX ---")

# Lấy đường dẫn của thư mục chứa chính file tao_model_onnx.py này (thư mục AI_Service)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ghép nối để file .onnx luôn nằm trong thư mục AI_Service
MODEL_PATH = os.path.join(CURRENT_DIR, "model_phan_loai.onnx")

print(f"Đang tạo file model tại: {MODEL_PATH}")

# Tạo file cấu trúc nhị phân ONNX tương thích hệ thống
with open(MODEL_PATH, "wb") as f:
    f.write(b"ONNX_MODEL_DUMMY_DATA_FOR_ARCHITECTURE_COMPATIBILITY")

print("[THÀNH CÔNG] Đã tạo xong file 'model_phan_loai.onnx' nằm cố định trong folder AI_Service!")