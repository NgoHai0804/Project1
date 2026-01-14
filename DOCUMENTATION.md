# Tài liệu Kỹ thuật - Hệ thống Nhận diện Phương tiện

## Tổng quan

Dự án này là một hệ thống nhận diện và theo dõi phương tiện thời gian thực sử dụng YOLOv8 và PyQt5. Hệ thống cho phép người dùng tải video, định nghĩa các vùng ROI (Region of Interest), và theo dõi các phương tiện trong các vùng đó.

## Công nghệ Sử dụng

### Thư viện Python Chính

| Thư viện | Phiên bản | Mục đích |
|----------|-----------|----------|
| **Python** | 3.8+ | Ngôn ngữ lập trình chính |
| **PyQt5** | 5.15+ | Framework giao diện đồ họa người dùng |
| **OpenCV (cv2)** | 4.5+ | Xử lý video, thao tác ảnh, vẽ overlay |
| **YOLOv8 (Ultralytics)** | Latest | Mô hình deep learning để nhận diện đối tượng |
| **Pandas** | Latest | Xử lý dữ liệu từ kết quả nhận diện YOLO |
| **NumPy** | Latest | Các phép toán số học và xử lý mảng |

### Công nghệ Nền tảng

- **YOLOv8**: Mô hình nhận diện đối tượng state-of-the-art, sử dụng kiến trúc CNN
- **PyQt5**: Framework GUI cross-platform dựa trên Qt
- **OpenCV**: Thư viện computer vision mạnh mẽ cho xử lý ảnh/video
- **COCO Dataset**: Dataset được sử dụng để train mô hình YOLO (80 classes)

## Cấu trúc File và Chức năng

### 1. `ui.py` - Giao diện Người dùng Chính

**Mô tả**: File chính chứa cửa sổ ứng dụng PyQt5, điều phối tất cả các thành phần.

**Chức năng chính**:
- Tạo và quản lý giao diện người dùng (MainWindow)
- Điều khiển video (play, pause, seek)
- Quản lý ROI (thêm, xóa, chỉnh sửa)
- Cấu hình nhận diện (confidence threshold, loại phương tiện)
- Hiển thị FPS và danh sách phương tiện
- Điều phối giữa các module khác

**Các class**:
- `MainWindow`: Class chính quản lý toàn bộ ứng dụng

**Thư viện sử dụng**:
```python
- PyQt5.QtWidgets: QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, 
                   QHBoxLayout, QListWidget, QCheckBox, QGroupBox, QFileDialog, 
                   QSlider, QSpinBox
- PyQt5.QtCore: QTimer, Qt
- cv2: Xử lý video
- time: Tính FPS
```

### 2. `detector.py` - Module Nhận diện Phương tiện

**Mô tả**: Module chứa logic nhận diện phương tiện sử dụng YOLOv8.

**Chức năng chính**:
- Khởi tạo và quản lý mô hình YOLOv8
- Nhận diện phương tiện trong frame video
- Lọc kết quả theo loại phương tiện và confidence threshold
- Cache kết quả để tối ưu hiệu suất (skip frames)
- Trả về bounding boxes với thông tin class và confidence

**Các class**:
- `VehicleDetector`: Class chính xử lý nhận diện

**Phương thức quan trọng**:
- `__init__()`: Khởi tạo mô hình YOLO, load class list
- `detect()`: Nhận diện phương tiện trong frame
- `set_confidence_threshold()`: Cập nhật ngưỡng confidence

**Thư viện sử dụng**:
```python
- ultralytics: YOLO model
- pandas: Xử lý dữ liệu từ YOLO results
```

**Cấu hình**:
- Model: `yolov8s.pt` (YOLOv8 small)
- Classes: Đọc từ `coco.txt`
- Default confidence: 40%
- Image size: 416x416 (có thể tùy chỉnh)

### 3. `tracker.py` - Module Theo dõi Đối tượng

**Mô tả**: Module implement thuật toán tracking đơn giản dựa trên khoảng cách Euclidean.

**Chức năng chính**:
- Gán ID duy nhất cho mỗi đối tượng
- Theo dõi vị trí đối tượng qua các frame
- Sử dụng khoảng cách tâm để match đối tượng giữa các frame
- Lưu lịch sử di chuyển của từng đối tượng

**Các class**:
- `Tracker`: Class tracking đối tượng

**Thuật toán**:
- Tính tâm của bounding box
- So sánh với các đối tượng đã track trước đó
- Match dựa trên khoảng cách Euclidean (max_distance)
- Tạo ID mới nếu không tìm thấy match

**Thư viện sử dụng**:
```python
- collections.defaultdict: Lưu trữ lịch sử tracking
- math: Tính khoảng cách Euclidean (math.hypot)
```

**Tham số**:
- `max_distance`: Khoảng cách tối đa để coi là cùng đối tượng (default: 40 pixels)
- `max_history`: Số điểm lịch sử tối đa lưu (default: 40)

### 4. `roi_manager.py` - Module Quản lý ROI

**Mô tả**: Module quản lý các vùng ROI (Region of Interest) và tracker riêng cho mỗi ROI.

**Chức năng chính**:
- Thêm, xóa, cập nhật ROI
- Quản lý tracker riêng cho mỗi ROI
- Lưu trữ thông tin các vehicle đã phát hiện trong ROI (saved_ids)
- Reset tracker khi cần thiết

**Các class**:
- `ROIManager`: Class quản lý ROI

**Cấu trúc dữ liệu**:
```python
rois = {
    roi_id: {
        'coords': (x1, y1, x2, y2),
        'tracker': Tracker(),
        'saved_ids': set()
    }
}
```

**Phương thức quan trọng**:
- `add_roi()`: Thêm ROI mới với tracker riêng
- `remove_roi()`: Xóa ROI
- `update_roi_coords()`: Cập nhật tọa độ ROI (reset tracker)
- `get_roi()`: Lấy thông tin ROI
- `reset_roi()`: Reset tracker của ROI

**Thư viện sử dụng**:
```python
- tracker.Tracker: Module tracker
```

### 5. `vehicle_processor.py` - Module Xử lý Phương tiện

**Mô tả**: Module xử lý và vẽ phương tiện trong các ROI, lưu ảnh phương tiện.

**Chức năng chính**:
- Xử lý vehicles trong từng ROI
- Lọc vehicles nằm trong ROI (dựa trên tâm bounding box)
- Vẽ bounding box, tâm, label cho mỗi vehicle
- Lưu ảnh vehicle lần đầu phát hiện
- Quản lý thống kê vehicles (đếm số frame xuất hiện)
- Trả về frame đã được vẽ

**Các class**:
- `VehicleProcessor`: Class xử lý vehicles

**Phương thức quan trọng**:
- `process_rois()`: Xử lý tất cả ROI và vẽ vehicles
- `get_vehicle_list()`: Lấy danh sách vehicles để hiển thị
- `reset_roi_vehicles()`: Reset vehicles của một ROI
- `reset_all()`: Reset tất cả vehicles

**Thư viện sử dụng**:
```python
- cv2: Vẽ bounding box, circle, text
- os: Tạo thư mục lưu ảnh
```

**Lưu trữ**:
- Thư mục mặc định: `Cars/`
- Format tên file: `roi{roi_id}_car_{vehicle_id}.jpg`

### 6. `video_widget.py` - Widget Hiển thị Video

**Mô tả**: Custom widget PyQt5 để hiển thị video frames.

**Chức năng chính**:
- Hiển thị frame video dạng QLabel
- Chuyển đổi OpenCV frame (BGR) sang QImage (RGB)
- Cập nhật frame mới

**Các class**:
- `VideoWidget`: Class widget hiển thị video

**Phương thức quan trọng**:
- `update_frame()`: Cập nhật frame mới để hiển thị

**Thư viện sử dụng**:
```python
- PyQt5.QtWidgets.QLabel: Widget cơ bản
- PyQt5.QtGui: QImage, QPixmap
- PyQt5.QtCore.Qt: Alignment
- cv2: Xử lý ảnh (cv2.cvtColor)
```

**Xử lý**:
- Chuyển BGR (OpenCV) → RGB (Qt)
- Convert numpy array → QImage → QPixmap

### 7. `coco.txt` - Danh sách Classes

**Mô tả**: File text chứa tên 80 classes của COCO dataset.

**Nội dung**:
- Mỗi dòng là tên một class
- Thứ tự tương ứng với class ID trong YOLO
- Classes liên quan phương tiện: person, bicycle, car, motorcycle, airplane, bus, train, truck, boat

### 8. `yolov8s.pt` - Mô hình YOLOv8

**Mô tả**: File trọng số mô hình YOLOv8 small đã được train trên COCO dataset.

**Đặc điểm**:
- Format: PyTorch (.pt)
- Architecture: YOLOv8s (small variant)
- Dataset: COCO (80 classes)
- Input size: Flexible (default 640x640)
- Auto-download: Tự động tải nếu thiếu

## Luồng Hoạt động

### 1. Khởi tạo Ứng dụng

```
ui.py (MainWindow.__init__)
  ├─> Khởi tạo ROIManager
  ├─> Khởi tạo VehicleProcessor
  ├─> setup_ui() → Tạo giao diện
  └─> init_detector() → Khởi tạo VehicleDetector (YOLO)
```

### 2. Mở Video

```
User click "Open Video"
  ├─> cv2.VideoCapture(file_path)
  ├─> Reset tất cả tracker và vehicles
  ├─> Khởi động timer (30ms)
  └─> Bắt đầu play video
```

### 3. Xử lý Frame (mỗi frame)

```
update_video() (timer callback)
  ├─> cv2.VideoCapture.read() → Đọc frame
  ├─> Resize frame
  ├─> Vẽ ROI overlay
  ├─> detector.detect() → Nhận diện phương tiện
  │     ├─> YOLO model.predict()
  │     ├─> Lọc theo target_classes
  │     └─> Return bounding boxes
  ├─> vehicle_processor.process_rois()
  │     ├─> Lọc vehicles trong ROI
  │     ├─> tracker.update() → Tracking
  │     ├─> Vẽ bounding box, label
  │     └─> Lưu ảnh vehicle (nếu lần đầu)
  ├─> Tính FPS
  ├─> Update vehicle list
  └─> video_widget.update_frame() → Hiển thị
```

### 4. Tracking Process

```
Tracker.update(objects_rect)
  ├─> Với mỗi bounding box:
  │     ├─> Tính tâm (cx, cy)
  │     ├─> Tìm object đã track có khoảng cách < max_distance
  │     ├─> Nếu tìm thấy: Gán ID cũ, cập nhật history
  │     └─> Nếu không: Tạo ID mới
  ├─> Giới hạn history (max_history)
  └─> Return [(x1, y1, x2, y2, id), ...]
```

### 5. Quản lý ROI

```
User thêm/chỉnh sửa ROI
  ├─> ROIManager.add_roi() / update_roi_coords()
  │     └─> Tạo Tracker mới cho ROI
  ├─> Update UI (list widget, spin boxes)
  └─> Reset vehicles của ROI
```

## Kiến trúc Hệ thống

```
┌─────────────────────────────────────────────────┐
│              ui.py (MainWindow)                 │
│  ┌──────────────────────────────────────────┐  │
│  │  VideoWidget    │   Control Panel        │  │
│  │  (Display)      │   (Settings/ROI List)  │  │
│  └──────────────────────────────────────────┘  │
└───────────────┬─────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐  ┌───▼────┐  ┌───▼──────────┐
│Vehicle│  │  ROI   │  │  Vehicle     │
│Detector│  │Manager │  │  Processor  │
│(YOLO) │  │        │  │              │
└───┬───┘  └───┬────┘  └───┬──────────┘
    │          │            │
    │      ┌───▼───┐        │
    │      │Tracker│        │
    │      │       │        │
    └──────┴───────┴────────┘
```

## Đặc điểm Kỹ thuật

### Tối ưu Hiệu suất

1. **Skip Frames**: Bỏ qua một số frame giữa các lần detect (mặc định: 2 frames)
2. **Detection Cache**: Lưu kết quả detect cuối cùng để tái sử dụng
3. **Image Size**: Giảm kích thước ảnh khi detect (416x416) để tăng tốc
4. **CPU Mode**: Sử dụng CPU thay vì GPU (có thể cấu hình)

### Xử lý ROI

- Mỗi ROI có tracker riêng
- Vehicles chỉ được đếm trong ROI nếu tâm nằm trong vùng
- Hỗ trợ nhiều ROI đồng thời
- Reset tracker khi thay đổi ROI

### Tracking Algorithm

- Thuật toán đơn giản dựa trên khoảng cách Euclidean
- Không sử dụng Kalman Filter hay DeepSORT
- Phù hợp cho video có ít occlusion (che khuất)
- ID được gán dựa trên vị trí tâm

## Hạn chế và Cải tiến

### Hạn chế Hiện tại

1. Tracking đơn giản: Dễ mất track khi occlusion cao
2. Không có object re-identification
3. Chỉ track dựa trên vị trí, không dùng appearance features
4. CPU-only: Chưa tối ưu GPU

### Gợi ý Cải tiến

1. Sử dụng DeepSORT hoặc ByteTrack cho tracking tốt hơn
2. Thêm Kalman Filter để dự đoán vị trí
3. Sử dụng appearance features (CNN) để re-identification
4. Tối ưu GPU với CUDA
5. Thêm tính năng đếm phương tiện (vehicle counting)
6. Thêm tính năng tính tốc độ phương tiện

