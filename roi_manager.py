from tracker import Tracker


class ROIManager:
    """Quản lý ROI (Region of Interest)"""
    
    def __init__(self):
        """Khởi tạo ROI manager"""
        self.rois = {}
        self.next_roi_id = 1
    
    def add_roi(self, x1, y1, x2, y2):
        """
        Thêm ROI mới
        
        Args:
            x1, y1, x2, y2: Tọa độ ROI
            
        Returns:
            roi_id: ID của ROI vừa tạo
        """
        roi_id = self.next_roi_id
        self.rois[roi_id] = {
            'coords': (x1, y1, x2, y2),
            'tracker': Tracker(),
            'saved_ids': set()
        }
        self.next_roi_id += 1
        return roi_id
    
    def remove_roi(self, roi_id):
        """Xóa ROI"""
        if roi_id in self.rois:
            del self.rois[roi_id]
            return True
        return False
    
    def update_roi_coords(self, roi_id, x1, y1, x2, y2):
        """Cập nhật tọa độ ROI"""
        if roi_id in self.rois:
            self.rois[roi_id]['coords'] = (x1, y1, x2, y2)
            self.rois[roi_id]['tracker'] = Tracker()
            self.rois[roi_id]['saved_ids'] = set()
            return True
        return False
    
    def get_roi(self, roi_id):
        """Lấy thông tin ROI"""
        return self.rois.get(roi_id)
    
    def get_all_rois(self):
        """Lấy tất cả ROI"""
        return self.rois
    
    def reset_roi(self, roi_id):
        """Reset tracker của ROI"""
        if roi_id in self.rois:
            self.rois[roi_id]['tracker'] = Tracker()
            self.rois[roi_id]['saved_ids'] = set()

