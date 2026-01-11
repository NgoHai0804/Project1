import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import os  # Thư viện thao tác file

# Tạo thư mục lưu ảnh xe nếu chưa tồn tại
if not os.path.exists("Cars"):
    os.makedirs("Cars")

# Load model YOLOv8
model = YOLO('yolov8s.pt')

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        colorsBGR = [x, y]
        print(colorsBGR)

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

cap = cv2.VideoCapture(r"D:\Project1\SampleVideo_LowQuality.mp4")

# Đọc danh sách class từ coco.txt
with open("coco.txt", "r") as f:
    class_list = f.read().split("\n")

count = 0
tracker = Tracker()

cy1 = 322
cy2 = 368
offset = 6

frame_num = 0  # Dùng để lưu ảnh theo frame

while True:    
    ret, frame = cap.read()
    if not ret:
        break
    count += 1
    if count % 3 != 0:  # Giảm tần suất xử lý
        continue
    frame = cv2.resize(frame, (1020, 500))
    frame_num += 1

    results = model.predict(frame)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")

    list_bbox = []

    for index, row in px.iterrows():
        x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
        d = int(row[5])
        c = class_list[d]
        
        if 'car' in c:
            list_bbox.append([x1, y1, x2, y2])

    bbox_id = tracker.update(list_bbox)

    for bbox in bbox_id:
        x3, y3, x4, y4, id = bbox
        cx, cy = (int(x3 + x4) // 2, int(y3 + y4) // 2)

        # Vẽ tâm và ID
        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
        cv2.putText(frame, str(id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

        # Cắt ảnh xe từ frame và lưu
        car_img = frame[y3:y4, x3:x4]  # Crop bounding box
        if car_img.size != 0:          # Kiểm tra crop không rỗng
            cv2.imwrite(f"Cars/car_{id}_frame{frame_num}.jpg", car_img)

    # Vẽ các đường tham chiếu
    cv2.line(frame, (274, cy1), (814, cy1), (255, 255, 255), 1)
    cv2.line(frame, (177, cy2), (927, cy2), (255, 255, 255), 1)

    cv2.imshow("RGB", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
