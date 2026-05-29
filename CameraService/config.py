# config.py
import os

# Địa chỉ API của dịch vụ tiếp theo (ví dụ: Backend hoặc AI Service)
# Thay đổi cổng (port) hoặc IP cho đúng với thực tế của nhóm
API_URL = "http://127.0.0.1:8000/upload-image"

# Kích thước ảnh chuẩn mà mô hình AI (TensorFlow/Keras) yêu cầu
TARGET_IMAGE_SIZE = (224, 224)

CAMERA_INDEX = 0