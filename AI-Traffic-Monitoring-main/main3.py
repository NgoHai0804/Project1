import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import Tracker
import os

class VideoLoader:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)
        self.frame_count = 0

    def read_frame(self, skip=3):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                return None
            self.frame_count += 1
            if self.frame_count % skip == 0:
                return frame

    def release(self):
        self.cap.release()


class YOLODetector:
    def __init__(self, model_path, class_file, target_classes=None):
        self.model = YOLO(model_path)
        with open(class_file, "r") as f:
            self.class_list = f.read().split("\n")
        # target_classes là danh sách tên lớp xe muốn nhận diện
        self.target_classes = target_classes if target_classes else ['car', 'bus', 'truck', 'motorcycle']

    def detect_cars(self, frame):
        results = self.model.predict(frame)
        boxes = results[0].boxes.data
        df = pd.DataFrame(boxes).astype(float)

        car_boxes = []
        for _, row in df.iterrows():
            x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
            cls_id = int(row[5])
            cls_name = self.class_list[cls_id]
            
            # Chỉ lưu box nếu nằm trong danh sách target_classes
            if cls_name in self.target_classes:
                car_boxes.append([x1, y1, x2, y2])

        return car_boxes



class ROIHandler:
    def __init__(self, x1, y1, x2, y2, save_dir="Cars"):
        self.roi = (x1, y1, x2, y2)
        self.tracker = Tracker()
        self.saved_ids = set()
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

    def crop(self, frame):
        x1, y1, x2, y2 = self.roi
        return frame[y1:y2, x1:x2]

    def apply_overlay(self, frame, alpha=0.2):
        x1, y1, x2, y2 = self.roi
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
        return frame

    def inside(self, x, y):
        x1, y1, x2, y2 = self.roi
        return x1 <= x <= x2 and y1 <= y <= y2

    def update_and_save(self, frame, boxes):
        x1_roi, y1_roi, _, _ = self.roi
        list_bbox = [[x1 + x1_roi, y1 + y1_roi, x2 + x1_roi, y2 + y1_roi] for x1, y1, x2, y2 in boxes]
        tracked = self.tracker.update(list_bbox)

        for x3, y3, x4, y4, id in tracked:
            cx, cy = (int(x3 + x4)//2, int(y3 + y4)//2)
            # Vẽ tâm
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

            # Vẽ ID
            cv2.putText(frame, str(id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 255), 2)

            # VẼ KHUNG VIỀN CHO XE
            cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 0), 1)  # màu xanh dương, dày 2 px

            if id not in self.saved_ids and self.inside(cx, cy):
                car_img = frame[y3:y4, x3:x4]
                if car_img.size != 0:
                    cv2.imwrite(f"{self.save_dir}/car_{id}.jpg", car_img)
                    self.saved_ids.add(id)



class CarDetectionApp:
    def __init__(self, video_path, model_path, class_file, target_cars, roi_list):
        """
        roi_list: danh sách tuple (x1, y1, x2, y2)
        """
        self.video = VideoLoader(video_path)
        self.detector = YOLODetector(model_path, class_file, target_cars)
        self.rois = [ROIHandler(*roi) for roi in roi_list]
        cv2.namedWindow('RGB')
        cv2.setMouseCallback('RGB', self.print_mouse_coords)

    @staticmethod
    def print_mouse_coords(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            print([x, y])

    def run(self):
        while True:
            frame = self.video.read_frame(skip=3)
            if frame is None:
                break

            frame = cv2.resize(frame, (1020, 500))

            for roi in self.rois:
                roi_frame = roi.crop(frame)
                boxes = self.detector.detect_cars(roi_frame)
                roi.update_and_save(frame, boxes)
                frame = roi.apply_overlay(frame)

            cv2.imshow("RGB", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.video.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    roi_coords_list = [
        # (0, 200, 350, 350), # x1, y1, x2, y2
        (0, 150, 600, 450), 
        # (700, 250, 1200, 500)   # ROI thứ 2
        # (100, 100, 300, 300)    # ROI thứ 3
    ]

    target_cars = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']  # chỉ nhận diện car và truck

    app = CarDetectionApp(
        video_path=r"data\input\YTSave.com_YouTube_4K-Road-traffic-video-for-object-detecti_Media_MNn9qKG2UFI_001_1080p.mp4",
        model_path="yolov8s.pt",
        class_file="coco.txt",
        target_cars=target_cars,
        roi_list=roi_coords_list
    )
    app.run()
