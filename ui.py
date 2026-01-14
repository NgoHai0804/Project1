import sys
import cv2
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QListWidget,
    QCheckBox, QGroupBox, QFileDialog, QSlider,
    QSpinBox
)
from PyQt5.QtCore import QTimer, Qt

from video_widget import VideoWidget
from detector import VehicleDetector
from roi_manager import ROIManager
from vehicle_processor import VehicleProcessor


class MainWindow(QWidget):
    """Main window cho Vehicle Detection Dashboard"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehicle Detection Dashboard")
        self.resize(1300, 720)

        self.cap = None
        self.total_frames = 0
        self.current_frame = 0
        self.is_playing = False
        
        self.frame_width = 900
        self.frame_height = 520
        
        self.model_path = "yolov8s.pt"
        self.class_file = "coco.txt"
        self.confidence_threshold = 40
        self.detect_skip_frames = 2
        self.detect_imgsz = 416
        
        self.detector = None
        self.roi_manager = ROIManager()
        self.vehicle_processor = VehicleProcessor()
        self.current_roi_id = None
        
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.current_fps = 0

        self.setup_ui()
        self.init_detector()

    def setup_ui(self):
        """Thiết lập giao diện"""
        self.video_widget = VideoWidget()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderMoved.connect(self.seek_video)

        self.btn_open = QPushButton("Open Video")
        self.btn_play = QPushButton("Play")
        self.btn_open.clicked.connect(self.open_video)
        self.btn_play.clicked.connect(self.toggle_play)

        self.tools_panel = self.create_tools_panel()

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.btn_open)
        top_bar.addWidget(self.btn_play)
        top_bar.addStretch()

        left_layout = QVBoxLayout()
        left_layout.addLayout(top_bar)
        left_layout.addWidget(self.video_widget)
        left_layout.addWidget(self.slider)

        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_layout, 3)
        main_layout.addWidget(self.tools_panel, 1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video)

    def init_detector(self):
        """Khởi tạo YOLO detector"""
        try:
            self.detector = VehicleDetector(
                model_path=self.model_path,
                class_file=self.class_file,
                confidence_threshold=self.confidence_threshold,
                detect_imgsz=self.detect_imgsz
            )
            
            self.roi_manager.add_roi(0, 100, 600, 400)
            self.update_roi_list()
            
            print("Detector initialized successfully!")
        except Exception as e:
            print(f"Error initializing detector: {e}")

    def get_target_classes(self):
        """Lấy danh sách loại phương tiện được chọn"""
        target_classes = []
        if self.cb_car.isChecked():
            target_classes.append('car')
        if self.cb_truck.isChecked():
            target_classes.append('truck')
        if self.cb_bus.isChecked():
            target_classes.append('bus')
        if self.cb_motor.isChecked():
            target_classes.append('motorcycle')
        return target_classes

    def create_tools_panel(self):
        """Tạo panel công cụ bên phải"""
        panel = QVBoxLayout()

        group_vehicle = QGroupBox("Loại phương tiện")
        vbox_vehicle = QVBoxLayout()
        self.cb_car = QCheckBox("Car")
        self.cb_truck = QCheckBox("Truck")
        self.cb_bus = QCheckBox("Bus")
        self.cb_motor = QCheckBox("Motorcycle")
        self.cb_car.setChecked(True)
        self.cb_truck.setChecked(True)
        self.cb_bus.setChecked(True)
        self.cb_motor.setChecked(True)
        self.cb_car.stateChanged.connect(self.reset_vehicle_list)
        self.cb_truck.stateChanged.connect(self.reset_vehicle_list)
        self.cb_bus.stateChanged.connect(self.reset_vehicle_list)
        self.cb_motor.stateChanged.connect(self.reset_vehicle_list)
        vbox_vehicle.addWidget(self.cb_car)
        vbox_vehicle.addWidget(self.cb_truck)
        vbox_vehicle.addWidget(self.cb_bus)
        vbox_vehicle.addWidget(self.cb_motor)
        
        hbox_conf = QHBoxLayout()
        hbox_conf.addWidget(QLabel("Confidence (%):"))
        self.spin_confidence = QSpinBox()
        self.spin_confidence.setMinimum(0)
        self.spin_confidence.setMaximum(100)
        self.spin_confidence.setValue(40)
        self.spin_confidence.setSuffix("%")
        self.spin_confidence.valueChanged.connect(self.on_confidence_changed)
        hbox_conf.addWidget(self.spin_confidence)
        vbox_vehicle.addLayout(hbox_conf)
        
        group_vehicle.setLayout(vbox_vehicle)

        group_roi = QGroupBox("Quản lý ROI")
        vbox_roi = QVBoxLayout()
        
        self.roi_list_widget = QListWidget()
        self.roi_list_widget.itemSelectionChanged.connect(self.on_roi_selected)
        vbox_roi.addWidget(QLabel("Danh sách ROI:"))
        vbox_roi.addWidget(self.roi_list_widget)
        
        hbox_roi_buttons = QHBoxLayout()
        self.btn_add_roi = QPushButton("Thêm ROI")
        self.btn_delete_roi = QPushButton("Xóa ROI")
        self.btn_add_roi.clicked.connect(self.on_add_roi_clicked)
        self.btn_delete_roi.clicked.connect(self.on_delete_roi_clicked)
        hbox_roi_buttons.addWidget(self.btn_add_roi)
        hbox_roi_buttons.addWidget(self.btn_delete_roi)
        vbox_roi.addLayout(hbox_roi_buttons)
        
        vbox_roi.addWidget(QLabel("Tọa độ ROI:"))
        hbox_x1 = QHBoxLayout()
        hbox_x1.addWidget(QLabel("X1:"))
        self.spin_x1 = QSpinBox()
        self.spin_x1.setMinimum(0)
        self.spin_x1.setMaximum(900)
        self.spin_x1.setValue(0)
        self.spin_x1.valueChanged.connect(self.on_roi_coords_changed)
        hbox_x1.addWidget(self.spin_x1)
        
        hbox_y1 = QHBoxLayout()
        hbox_y1.addWidget(QLabel("Y1:"))
        self.spin_y1 = QSpinBox()
        self.spin_y1.setMinimum(0)
        self.spin_y1.setMaximum(520)
        self.spin_y1.setValue(0)
        self.spin_y1.valueChanged.connect(self.on_roi_coords_changed)
        hbox_y1.addWidget(self.spin_y1)
        
        hbox_x2 = QHBoxLayout()
        hbox_x2.addWidget(QLabel("X2:"))
        self.spin_x2 = QSpinBox()
        self.spin_x2.setMinimum(0)
        self.spin_x2.setMaximum(900)
        self.spin_x2.setValue(600)
        self.spin_x2.valueChanged.connect(self.on_roi_coords_changed)
        hbox_x2.addWidget(self.spin_x2)
        
        hbox_y2 = QHBoxLayout()
        hbox_y2.addWidget(QLabel("Y2:"))
        self.spin_y2 = QSpinBox()
        self.spin_y2.setMinimum(0)
        self.spin_y2.setMaximum(520)
        self.spin_y2.setValue(400)
        self.spin_y2.valueChanged.connect(self.on_roi_coords_changed)
        hbox_y2.addWidget(self.spin_y2)
        
        vbox_roi.addLayout(hbox_x1)
        vbox_roi.addLayout(hbox_y1)
        vbox_roi.addLayout(hbox_x2)
        vbox_roi.addLayout(hbox_y2)
        
        group_roi.setLayout(vbox_roi)

        group_list = QGroupBox("Xe trong ROI")
        vbox_list = QVBoxLayout()
        self.list_widget = QListWidget()
        vbox_list.addWidget(self.list_widget)
        group_list.setLayout(vbox_list)

        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("font-weight: bold; color: green;")

        panel.addWidget(group_vehicle)
        panel.addWidget(group_roi)
        panel.addWidget(group_list)
        panel.addWidget(self.fps_label)
        panel.addStretch()

        wrapper = QWidget()
        wrapper.setLayout(panel)
        return wrapper

    def on_confidence_changed(self, value):
        """Khi confidence threshold thay đổi"""
        self.confidence_threshold = value
        if self.detector:
            self.detector.set_confidence_threshold(value)
        self.reset_vehicle_list()

    def reset_vehicle_list(self):
        """Reset danh sách vehicles khi thay đổi loại phương tiện"""
        self.vehicle_processor.reset_all()
        rois = self.roi_manager.get_all_rois()
        for roi_id in rois:
            self.roi_manager.reset_roi(roi_id)

    def update_roi_list(self):
        """Cập nhật danh sách ROI trong list widget"""
        self.roi_list_widget.clear()
        rois = self.roi_manager.get_all_rois()
        for roi_id in sorted(rois.keys()):
            x1, y1, x2, y2 = rois[roi_id]['coords']
            item_text = f"ROI {roi_id}: ({x1}, {y1}) -> ({x2}, {y2})"
            self.roi_list_widget.addItem(item_text)

    def on_roi_selected(self):
        """Khi chọn ROI từ list"""
        selected_items = self.roi_list_widget.selectedItems()
        if not selected_items:
            self.current_roi_id = None
            self.clear_roi_editor()
            return
        
        text = selected_items[0].text()
        roi_id = int(text.split()[1].replace(':', ''))
        
        roi_data = self.roi_manager.get_roi(roi_id)
        if roi_data:
            self.current_roi_id = roi_id
            x1, y1, x2, y2 = roi_data['coords']
            self.spin_x1.blockSignals(True)
            self.spin_y1.blockSignals(True)
            self.spin_x2.blockSignals(True)
            self.spin_y2.blockSignals(True)
            self.spin_x1.setValue(x1)
            self.spin_y1.setValue(y1)
            self.spin_x2.setValue(x2)
            self.spin_y2.setValue(y2)
            self.spin_x1.blockSignals(False)
            self.spin_y1.blockSignals(False)
            self.spin_x2.blockSignals(False)
            self.spin_y2.blockSignals(False)

    def clear_roi_editor(self):
        """Xóa thông tin trong ROI editor"""
        self.spin_x1.blockSignals(True)
        self.spin_y1.blockSignals(True)
        self.spin_x2.blockSignals(True)
        self.spin_y2.blockSignals(True)
        self.spin_x1.setValue(0)
        self.spin_y1.setValue(0)
        self.spin_x2.setValue(0)
        self.spin_y2.setValue(0)
        self.spin_x1.blockSignals(False)
        self.spin_y1.blockSignals(False)
        self.spin_x2.blockSignals(False)
        self.spin_y2.blockSignals(False)

    def on_roi_coords_changed(self):
        """Khi tọa độ ROI thay đổi"""
        if self.current_roi_id:
            x1 = self.spin_x1.value()
            y1 = self.spin_y1.value()
            x2 = self.spin_x2.value()
            y2 = self.spin_y2.value()
            
            if x1 >= x2 or y1 >= y2:
                return
            
            self.roi_manager.update_roi_coords(self.current_roi_id, x1, y1, x2, y2)
            self.vehicle_processor.reset_roi_vehicles(self.current_roi_id)
            self.roi_list_widget.blockSignals(True)
            self.update_roi_list()
            for i in range(self.roi_list_widget.count()):
                item = self.roi_list_widget.item(i)
                if f"ROI {self.current_roi_id}:" in item.text():
                    self.roi_list_widget.setCurrentItem(item)
                    break
            self.roi_list_widget.blockSignals(False)

    def on_add_roi_clicked(self):
        """Thêm ROI mới với tọa độ mặc định"""
        x1, y1 = 0, 0
        x2, y2 = 200, 200
        roi_id = self.roi_manager.add_roi(x1, y1, x2, y2)
        self.current_roi_id = roi_id
        self.spin_x1.blockSignals(True)
        self.spin_y1.blockSignals(True)
        self.spin_x2.blockSignals(True)
        self.spin_y2.blockSignals(True)
        self.spin_x1.setValue(x1)
        self.spin_y1.setValue(y1)
        self.spin_x2.setValue(x2)
        self.spin_y2.setValue(y2)
        self.spin_x1.blockSignals(False)
        self.spin_y1.blockSignals(False)
        self.spin_x2.blockSignals(False)
        self.spin_y2.blockSignals(False)
        self.roi_list_widget.blockSignals(True)
        self.update_roi_list()
        for i in range(self.roi_list_widget.count()):
            item = self.roi_list_widget.item(i)
            if f"ROI {roi_id}:" in item.text():
                self.roi_list_widget.setCurrentItem(item)
                break
        self.roi_list_widget.blockSignals(False)

    def on_delete_roi_clicked(self):
        """Xóa ROI được chọn"""
        if self.current_roi_id:
            self.roi_manager.remove_roi(self.current_roi_id)
            self.vehicle_processor.reset_roi_vehicles(self.current_roi_id)
            self.update_roi_list()
            if self.current_roi_id:
                self.current_roi_id = None
                self.clear_roi_editor()

    def update_vehicle_list(self):
        """Cập nhật danh sách vehicles trong list widget"""
        self.list_widget.clear()
        vehicle_list = self.vehicle_processor.get_vehicle_list()
        for item_text in vehicle_list:
            self.list_widget.addItem(item_text)

    def open_video(self):
        """Mở video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn video", "", "Video Files (*.mp4 *.avi *.mov)"
        )
        if not file_path:
            return

        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(file_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.slider.setMaximum(self.total_frames)
        self.current_frame = 0
        
        self.vehicle_processor.reset_all()
        rois = self.roi_manager.get_all_rois()
        for roi_id in rois:
            self.roi_manager.reset_roi(roi_id)
        self.list_widget.clear()
        if self.detector:
            self.detector.last_detect_frame = -1
            self.detector.last_detections = []
        self.fps_frame_count = 0
        self.fps_start_time = time.time()
        
        self.is_playing = True
        self.btn_play.setText("Pause")
        self.timer.start(30)

    def toggle_play(self):
        """Play/Pause video"""
        if not self.cap:
            return

        self.is_playing = not self.is_playing
        if self.is_playing:
            self.timer.start(30)
            self.btn_play.setText("Pause")
        else:
            self.timer.stop()
            self.btn_play.setText("Play")

    def seek_video(self, frame_id):
        """Seek đến frame cụ thể"""
        if not self.cap:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        self.current_frame = frame_id
        
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            
            rois = self.roi_manager.get_all_rois()
            for roi_id, roi_data in rois.items():
                x1, y1, x2, y2 = roi_data['coords']
                overlay = frame.copy()
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)
                cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
                color = ((roi_id * 50) % 255, (roi_id * 80) % 255, (roi_id * 120) % 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
                cv2.putText(frame, f"ROI {roi_id}", (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 2)
            
            if self.detector:
                target_classes = self.get_target_classes()
                vehicle_boxes = self.detector.detect(frame, target_classes, self.current_frame, self.detect_skip_frames, force=True)
                if vehicle_boxes:
                    for box in vehicle_boxes:
                        x1, y1, x2, y2, cls_name, conf = box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)
                        conf_percent = int(conf * 100)
                        label = f"{cls_name} {conf_percent}%"
                        cv2.putText(frame, label, (x1, y1 - 10), 
                                   cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1)
            
            self.video_widget.update_frame(frame)

    def update_video(self):
        """Cập nhật video frame"""
        if not self.cap or not self.is_playing:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            return

        self.current_frame += 1
        self.slider.blockSignals(True)
        self.slider.setValue(self.current_frame)
        self.slider.blockSignals(False)

        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        
        rois = self.roi_manager.get_all_rois()
        if rois:
            overlay = frame.copy()
            for roi_id, roi_data in rois.items():
                x1, y1, x2, y2 = roi_data['coords']
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)
            cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
            
            for roi_id, roi_data in rois.items():
                x1, y1, x2, y2 = roi_data['coords']
                color = ((roi_id * 50) % 255, (roi_id * 80) % 255, (roi_id * 120) % 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
                cv2.putText(frame, f"ROI {roi_id}", (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 2)
        
        if self.detector:
            target_classes = self.get_target_classes()
            vehicle_boxes = self.detector.detect(frame, target_classes, self.current_frame, self.detect_skip_frames)
            
            if vehicle_boxes:
                frame = self.vehicle_processor.process_rois(frame, vehicle_boxes, rois)
        
        self.fps_frame_count += 1
        if self.current_frame % 30 == 0:
            elapsed = time.time() - self.fps_start_time
            if elapsed > 0:
                self.current_fps = 30 / elapsed
                self.fps_label.setText(f"FPS: {self.current_fps:.1f}")
            self.fps_start_time = time.time()
        
        if self.current_frame % 30 == 0:
            self.update_vehicle_list()
        
        self.video_widget.update_frame(frame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
