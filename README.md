# 🚗 Vehicle Detection Dashboard

<p align="center">
   <b>Hệ thống Nhận diện và Theo dõi Phương tiện Thời gian Thực với Giao diện PyQt5</b>  
</p>

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-red.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-orange.svg)

## ✨ Tổng quan

Dự án này là một **hệ thống nhận diện và theo dõi phương tiện thời gian thực** với giao diện đồ họa PyQt5 trực quan. Hệ thống sử dụng **YOLOv8** để nhận diện và theo dõi các phương tiện trong video, cung cấp dữ liệu hữu ích cho việc giám sát và phân tích giao thông.

Ứng dụng có giao diện hiện đại cho phép người dùng:
- Tải và phát video
- Cấu hình thiết lập nhận diện (loại phương tiện, ngưỡng độ tin cậy)
- Quản lý nhiều vùng ROI (Region of Interest)
- Theo dõi phương tiện trong các vùng chỉ định
- Xem FPS và thống kê phương tiện thời gian thực

## 📸 Ảnh Kết quả

![Vehicle Detection Dashboard](https://cdn.notegpt.io/notegpt/web3in1/chat/13b051c0-feca-4744-aa36-5e49dacdd146.jpg)

*Giao diện ứng dụng đang hoạt động với nhận diện phương tiện trong ROI*

## 🌟 Tính năng

### Chức năng chính
✅ **Nhận diện Phương tiện Thời gian Thực** sử dụng YOLOv8  
✅ **Hỗ trợ Nhiều ROI** - Định nghĩa và quản lý nhiều vùng theo dõi  
✅ **Theo dõi Phương tiện** - Theo dõi phương tiện qua các frame với ID duy nhất  
✅ **Cấu hình Nhận diện** - Chọn loại phương tiện (Xe hơi, Xe tải, Xe buýt, Xe máy)  
✅ **Ngưỡng Độ tin cậy** - Điều chỉnh độ nhạy nhận diện  
✅ **Tối ưu FPS** - Bỏ qua frame và tối ưu kích thước ảnh để cải thiện hiệu suất  
✅ **Thống kê Phương tiện** - Thông tin đếm và theo dõi thời gian thực  
✅ **Tự động Lưu Ảnh** - Tự động lưu ảnh phương tiện đã nhận diện  

### Giao diện Người dùng
✅ **Giao diện PyQt5 Hiện đại** - Giao diện sạch sẽ và trực quan  
✅ **Điều khiển Video** - Phát, tạm dừng và tua video  
✅ **Quản lý ROI** - Thêm, xóa và chỉnh sửa vùng ROI với điều khiển tọa độ  
✅ **Hiển thị FPS Thời gian Thực** - Theo dõi hiệu suất hệ thống  
✅ **Danh sách Phương tiện** - Xem tất cả phương tiện đã theo dõi với chi tiết  

## 💻 Công nghệ Sử dụng

| Công nghệ | Mục đích |
|------------|---------|
| **Python 3.8+** | Ngôn ngữ lập trình chính |
| **PyQt5** | Giao diện đồ họa người dùng |
| **YOLOv8 (Ultralytics)** | Mô hình nhận diện đối tượng |
| **OpenCV** | Xử lý video và thao tác ảnh |
| **Pandas** | Xử lý dữ liệu kết quả nhận diện |
| **NumPy** | Các phép toán số học |

## 📁 Cấu trúc Dự án

```
Project1/
├── ui.py                    # Cửa sổ ứng dụng chính (PyQt5)
├── video_widget.py          # Widget hiển thị video
├── detector.py              # Logic nhận diện YOLO
├── roi_manager.py           # Quản lý ROI (Region of Interest)
├── vehicle_processor.py     # Xử lý và theo dõi phương tiện
├── tracker.py               # Thuật toán theo dõi phương tiện
├── coco.txt                 # Tên các lớp COCO
├── yolov8s.pt              # Trọng số mô hình YOLOv8
├── Cars/                   # Thư mục lưu ảnh phương tiện
├── data/
│   ├── input/              # File video đầu vào
│   └── output/             # File video đầu ra
└── README.md               # File này
```

## 🚀 Cài đặt & Sử dụng

### Yêu cầu Hệ thống

- Python 3.8 trở lên
- pip package manager

### Các bước Cài đặt

1. **Clone hoặc tải repository**

2. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install ultralytics opencv-python PyQt5 pandas numpy
   ```

3. **Tải mô hình YOLOv8** (nếu chưa có):
   - File mô hình `yolov8s.pt` nên có trong thư mục gốc dự án
   - Sẽ tự động tải xuống khi chạy lần đầu nếu thiếu

4. **Chuẩn bị file video:**
   - Đặt các file video vào thư mục `data/input/`
   - Định dạng hỗ trợ: `.mp4`, `.avi`, `.mov`

### Chạy Ứng dụng

1. **Khởi động ứng dụng:**
   ```bash
   python ui.py
   ```

2. **Sử dụng Giao diện:**
   - Nhấp **"📂 Open Video"** để tải file video
   - Sử dụng **"▶ Play"** / **"⏸ Pause"** để điều khiển phát
   - Điều chỉnh **Confidence (%)** để lọc kết quả nhận diện
   - Chọn loại phương tiện bằng các checkbox (Car, Truck, Bus, Motorcycle)
   - **Thêm ROI** để định nghĩa vùng theo dõi
   - **Chỉnh sửa ROI** bằng các spin box tọa độ
   - Xem phương tiện đã theo dõi trong danh sách "Xe trong ROI"

### Cấu hình

#### Chọn Loại Phương tiện
- Bật/tắt các checkbox để bật/tắt nhận diện cho từng loại phương tiện
- Thay đổi có hiệu lực ngay lập tức

#### Ngưỡng Độ tin cậy
- Điều chỉnh phần trăm (0-100%) để lọc kết quả nhận diện
- Giá trị cao hơn = ít kết quả hơn nhưng chính xác hơn
- Giá trị thấp hơn = nhiều kết quả hơn bao gồm cả những kết quả ít tin cậy

#### Quản lý ROI
- **Thêm ROI**: Nhấp "➕ Thêm ROI" để tạo vùng theo dõi mới
- **Chỉnh sửa ROI**: Chọn ROI từ danh sách, điều chỉnh tọa độ X1, Y1, X2, Y2
- **Xóa ROI**: Chọn ROI và nhấp "➖ Xóa ROI"
- Mỗi ROI có bộ theo dõi và đếm phương tiện riêng

## 🎓 Chi tiết Kỹ thuật

### Quy trình Nhận diện

1. **Tải Frame**: Video frame được tải và resize về 900x520
2. **Nhận diện YOLO**: Frame được xử lý bởi YOLOv8 (mỗi N frame để tối ưu)
3. **Lọc**: Kết quả nhận diện được lọc theo:
   - Loại phương tiện đã chọn
   - Ngưỡng độ tin cậy
   - Ranh giới ROI
4. **Theo dõi**: Phương tiện được theo dõi bằng thuật toán tracker tùy chỉnh
5. **Hiển thị**: Vẽ bounding box, ID và nhãn lên frame
6. **Thống kê**: Cập nhật số lượng và thông tin phương tiện

### Tối ưu Hiệu suất

- **Bỏ qua Frame**: Nhận diện chạy mỗi 2-4 frame (có thể cấu hình)
- **Kích thước Ảnh**: Nhận diện sử dụng đầu vào 416x416 (nhanh hơn độ phân giải đầy đủ)
- **Cache Kết quả**: Kết quả được cache giữa các frame
- **Render Hiệu quả**: Overlay ROI được tối ưu

### Trách nhiệm Module

- **`ui.py`**: Cửa sổ chính, thành phần UI, xử lý sự kiện
- **`detector.py`**: Tải mô hình YOLO, thực thi nhận diện, lọc kết quả
- **`roi_manager.py`**: Tạo ROI, xóa, quản lý tọa độ
- **`vehicle_processor.py`**: Theo dõi phương tiện, hiển thị, lưu ảnh
- **`video_widget.py`**: Widget hiển thị frame video
- **`tracker.py`**: Thuật toán theo dõi đối tượng nhiều

## 📊 Trường hợp Sử dụng

### Giám sát Giao thông
- Theo dõi lưu lượng phương tiện trong các khu vực đường cụ thể
- Đếm phương tiện đi qua các điểm kiểm tra
- Phân tích mô hình giao thông

### An ninh & Giám sát
- Theo dõi phương tiện trong bãi đỗ xe
- Giám sát khu vực hạn chế
- Nhận diện và ghi log phương tiện

### Nghiên cứu & Phân tích
- Thu thập dữ liệu phương tiện cho nghiên cứu
- Phân tích hành vi giao thông
- Tạo thống kê và báo cáo

## 🔧 Tùy chỉnh

### Điều chỉnh Thiết lập Nhận diện

Chỉnh sửa `ui.py` để thay đổi giá trị mặc định:
```python
self.confidence_threshold = 40  # Ngưỡng độ tin cậy mặc định %
self.detect_skip_frames = 2     # Số frame bỏ qua giữa các lần nhận diện
self.detect_imgsz = 416         # Kích thước ảnh nhận diện
```

### Thay đổi Mô hình

Thay thế `yolov8s.pt` bằng các mô hình YOLOv8 khác:
- `yolov8n.pt` - Nano (nhanh nhất, ít chính xác)
- `yolov8m.pt` - Medium (cân bằng)
- `yolov8l.pt` - Large (chậm hơn, chính xác hơn)
- `yolov8x.pt` - Extra Large (chậm nhất, chính xác nhất)

## 🐛 Xử lý Sự cố

### Các Vấn đề Thường gặp

**Vấn đề**: Không tìm thấy file mô hình
- **Giải pháp**: Đảm bảo `yolov8s.pt` có trong thư mục gốc dự án, hoặc nó sẽ tự động tải xuống

**Vấn đề**: FPS thấp
- **Giải pháp**: 
  - Tăng giá trị `detect_skip_frames`
  - Giảm `detect_imgsz` (ví dụ: 320 thay vì 416)
  - Sử dụng mô hình YOLO nhỏ hơn (yolov8n.pt)

**Vấn đề**: Không có kết quả nhận diện
- **Giải pháp**: 
  - Giảm ngưỡng độ tin cậy
  - Đảm bảo các checkbox loại phương tiện đã được chọn
  - Kiểm tra tọa độ ROI có đúng không

**Vấn đề**: Lỗi import PyQt5
- **Giải pháp**: Cài đặt PyQt5: `pip install PyQt5`

## 📝 Ghi chú

- Ảnh phương tiện được tự động lưu vào thư mục `Cars/`
- Mỗi ROI theo dõi phương tiện độc lập
- Kết quả nhận diện được cache để tối ưu hiệu suất
- FPS được tính toán và hiển thị mỗi 30 frame

## 🤝 Đóng góp

Đóng góp rất được hoan nghênh! Hãy thoải mái:
- Báo cáo lỗi
- Đề xuất tính năng mới
- Gửi pull request
- Cải thiện tài liệu

## 📄 Giấy phép

Dự án này là mã nguồn mở và có sẵn cho mục đích giáo dục và nghiên cứu.

## 🙏 Lời cảm ơn

- **Ultralytics** cho YOLOv8
- Cộng đồng **OpenCV**
- Các nhà phát triển **PyQt5**

---

**Được tạo với ❤️ cho giám sát giao thông và nhận diện phương tiện**
