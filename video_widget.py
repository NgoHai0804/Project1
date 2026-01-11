import cv2
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt


class VideoWidget(QLabel):
    """Widget để hiển thị video frame"""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(800, 500)
        self.setStyleSheet("background:black;")

    def update_frame(self, frame):
        """Cập nhật frame hiển thị"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.setPixmap(pix)

