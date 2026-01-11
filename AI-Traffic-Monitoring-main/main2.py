import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import os

# --- Tạo thư mục lưu ảnh xe nếu chưa tồn tại ---
if not os.path.exists("Cars"):
    os.makedirs("Cars")

# --- Load model YOLOv8 ---
model = YOLO('yolov8s.pt')

# --- Hàm in tọa độ chuột ---
def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        print([x, y])

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

cap = cv2.VideoCapture(r"D:\Project1\SampleVideo_LowQuality.mp4")

# --- Đọc danh sách class từ coco.txt ---
with open("coco.txt", "r") as f:
    class_list = f.read().split("\n")

count = 0
frame_num = 0
tracker = Tracker()
saved_ids = set()  # Lưu ID xe đã chụp

# --- Vùng nhận diện tổng thể (ROI) --- 
# Format: (x1, y1, x2, y2)
roi_x1, roi_y1, roi_x2, roi_y2 = 200, 300, 800, 700  # ví dụ vùng quan tâm

while True:
    ret, frame = cap.read()
    if not ret:
        break
    count += 1
    if count % 3 != 0:
        continue

    frame = cv2.resize(frame, (1020, 500))
    frame_num += 1

    # --- Crop frame theo ROI trước khi dự đoán ---
    roi_frame = frame[roi_y1:roi_y2, roi_x1:roi_x2]

    # --- Dự đoán trong ROI ---
    results = model.predict(roi_frame)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")

    list_bbox = []

    for index, row in px.iterrows():
        x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
        d = int(row[5])
        c = class_list[d]

        if 'car' in c:
            # --- Chuyển tọa độ từ ROI về frame gốc ---
            list_bbox.append([x1 + roi_x1, y1 + roi_y1, x2 + roi_x1, y2 + roi_y1])

    # --- Cập nhật tracker ---
    bbox_id = tracker.update(list_bbox)

    for bbox in bbox_id:
        x3, y3, x4, y4, id = bbox
        cx, cy = (int(x3 + x4) // 2, int(y3 + y4) // 2)

        # Vẽ tâm và ID
        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
        cv2.putText(frame, str(id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

        # Chỉ lưu xe nếu ID chưa có trong set và tâm xe nằm trong ROI
        if id not in saved_ids and roi_x1 <= cx <= roi_x2 and roi_y1 <= cy <= roi_y2:
            car_img = frame[y3:y4, x3:x4]
            if car_img.size != 0:
                cv2.imwrite(f"Cars/car_{id}.jpg", car_img)
                saved_ids.add(id)

    # --- Vẽ vùng ROI trên frame ---
    overlay = frame.copy()
    alpha = 0.2
    cv2.rectangle(overlay, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 0, 255), 2)  # viền đỏ

    cv2.imshow("RGB", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
