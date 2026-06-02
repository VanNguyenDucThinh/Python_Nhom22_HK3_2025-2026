import cv2

def quet_tim_index_camera():
    index_hop_le = []
    print("Khởi động quét camera... Vui lòng đợi vài giây...")
    
    for i in range(10):
        cap = cv2.VideoCapture(i)
        # Nếu camera mở thành công
        if cap.isOpened():
            # Lấy thử tên hoặc độ phân giải để kiểm tra
            w = cap.get(cv2.shape[1] if hasattr(cv2, 'shape') else 3)
            h = cap.get(cv2.shape[0] if hasattr(cv2, 'shape') else 4)
            print(f"-> Tìm thấy Camera tại INDEX: {i} (Độ phân giải: {int(w)}x{int(h)})")
            index_hop_le.append(i)
            cap.release() # Đóng camera lại để giải phóng bộ nhớ
            
    if not index_hop_le:
        print("Không tìm thấy bất kỳ camera nào đang kết nối!")
    else:
        print(f"\n==> CÁC BIẾN SỐ CAMERA BẠN CÓ THỂ DÙNG LÀ: {index_hop_le}")
    return index_hop_le

quet_tim_index_camera()