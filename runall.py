import subprocess
import os
import sys
import time

# Xác định chính xác đường dẫn gốc dự án
goc_du_an = os.path.abspath(os.getcwd())

print("=" * 60)
print("🚀 HỆ THỐNG KÍCH HOẠT DỰ ÁN TỰ ĐỘNG KHÉP KÍN 🚀")
print("=" * 60)
print(f"📁 Thư mục đang đứng: {goc_du_an}\n")

# 1. Bật Backend Service (Cổng 5000)
path_backend = os.path.join(goc_du_an, "Backend", "backend_service.py")
print("⚡ 1. Đang khởi động Backend Service...")
process_backend = subprocess.Popen([sys.executable, path_backend])
time.sleep(2) 

# 2. Bật AI Service (Cổng 8000)
path_ai = os.path.join(goc_du_an, "AI_Service", "ai_service.py")
print("🧠 2. Đang khởi động AI Service...")
process_ai = subprocess.Popen([sys.executable, path_ai])
time.sleep(3) 

# 3. Bật Giao diện Camera chính
path_camera = os.path.join(goc_du_an, "UI", "main_app.py")
print("📸 3. Đang mở Giao diện Camera chính...")
print("-" * 60)

try:
    # Cấu hình giải phóng luồng hiển thị đồ họa và bắt log lỗi nếu sập
    result = subprocess.run(
        [sys.executable, path_camera],
        capture_output=True,  # Bật lại để tóm gọn lỗi nội bộ của main.py nếu có
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    
    if result.returncode != 0:
        print("\n❌ [LỖI NỘI BỘ MAIN.PY] File giao diện bị sập! Chi tiết nguyên nhân:")
        print("-" * 50)
        print(result.stderr)
        print("-" * 50)
    else:
        print("\n[THÔNG BÁO] Bạn đã chủ động đóng Giao diện chính.")

except KeyboardInterrupt:
    print("\n[THÔNG BÁO] Người dùng ngắt từ bàn phím.")

finally:
    # Dọn dẹp cổng kết nối an toàn khi kết thúc
    print("\n" + "=" * 60)
    print("⚠️ Đang đóng các dịch vụ chạy ngầm giải phóng bộ nhớ...")
    try:
        process_backend.terminate()
        print("[ĐÃ TẮT] Đã đóng cổng Backend (5000)")
    except:
        pass
    try:
        process_ai.terminate()
        print("[ĐÃ TẮT] Đã đóng cổng AI Service (8000)")
    except:
        pass
    print("🥳 HỆ THỐNG ĐÃ ĐƯỢC GIẢI PHÓNG AN TOÀN!")
    print("=" * 60)