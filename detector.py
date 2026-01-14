import pandas as pd
from ultralytics import YOLO


class VehicleDetector:
    """Class để nhận diện phương tiện sử dụng YOLO"""
    
    def __init__(self, model_path, class_file, confidence_threshold=40, detect_imgsz=416):
        """
        Khởi tạo detector
        
        Args:
            model_path: Đường dẫn đến file model YOLO (.pt)
            class_file: Đường dẫn đến file danh sách class (coco.txt)
            confidence_threshold: Ngưỡng confidence (%)
            detect_imgsz: Kích thước ảnh khi detect (nhỏ hơn = nhanh hơn)
        """
        self.model_path = model_path
        self.class_file = class_file
        self.confidence_threshold = confidence_threshold
        self.detect_imgsz = detect_imgsz
        
        with open(class_file, "r") as f:
            self.class_list = f.read().split("\n")
        
        self.yolo_model = YOLO(model_path)
        
        self.last_detect_frame = -1
        self.last_detections = []
    
    def set_confidence_threshold(self, threshold):
        """Thay đổi confidence threshold"""
        self.confidence_threshold = threshold
        self.last_detect_frame = -1
        self.last_detections = []
    
    def detect(self, frame, target_classes, current_frame, detect_skip_frames=2, force=False):
        """
        Nhận diện phương tiện trong frame
        
        Args:
            frame: Frame cần detect (numpy array)
            target_classes: Danh sách loại phương tiện cần detect ['car', 'truck', ...]
            current_frame: Số frame hiện tại
            detect_skip_frames: Số frames bỏ qua giữa các lần detect
            force: Buộc detect ngay cả khi skip frames
            
        Returns:
            List các bounding boxes: [[x1, y1, x2, y2, cls_name, confidence], ...]
        """
        if not force and (current_frame - self.last_detect_frame) < detect_skip_frames:
            return self.last_detections
        
        if not target_classes:
            self.last_detections = []
            return []
        
        conf_threshold = self.confidence_threshold / 100.0
        results = self.yolo_model.predict(
            frame,                 # Ảnh đầu vào
            verbose=False,         # Tắt log
            imgsz=self.detect_imgsz,  # Kích thước resize ảnh
            conf=conf_threshold,   # Ngưỡng độ tin cậy
            half=False,            # Không dùng FP16 (CPU)
            device='cpu'           # Chạy trên CPU
        )

        boxes = results[0].boxes.data
        df = pd.DataFrame(boxes).astype(float)

        vehicle_boxes = []
        for _, row in df.iterrows():
            x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
            cls_id = int(row[5]) # id trong danh sách coco
            confidence = float(row[4]) # tỷ lệ %
            
            if cls_id < len(self.class_list):
                cls_name = self.class_list[cls_id]
                
                if cls_name in target_classes and confidence >= conf_threshold:
                    vehicle_boxes.append([x1, y1, x2, y2, cls_name, confidence])
        
        self.last_detections = vehicle_boxes
        self.last_detect_frame = current_frame
        
        return vehicle_boxes

