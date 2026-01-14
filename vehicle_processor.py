import cv2
import os


class VehicleProcessor:
    """Xử lý và tracking vehicles trong ROI"""
    
    def __init__(self, save_dir="Cars"):
        """
        Khởi tạo processor
        
        Args:
            save_dir: Thư mục lưu ảnh vehicles
        """
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        self.detected_vehicles = {}
    
    def process_rois(self, frame, vehicle_boxes, rois):
        """
        Xử lý tất cả ROI và tracking vehicles
        
        Args:
            frame: Frame cần xử lý
            vehicle_boxes: Danh sách vehicles đã detect [[x1, y1, x2, y2, cls_name, conf], ...]
            rois: Dictionary các ROI từ ROIManager
            
        Returns:
            Frame đã được vẽ vehicles
        """
        if not vehicle_boxes or not rois:
            return frame
        
        for roi_id, roi_data in rois.items():
            x1_roi, y1_roi, x2_roi, y2_roi = roi_data['coords']
            tracker = roi_data['tracker']
            saved_ids = roi_data['saved_ids']
            
            roi_boxes = []
            vehicle_info_map = []
            
            for box in vehicle_boxes:
                x1, y1, x2, y2, cls_name, conf = box
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                if x1_roi <= cx <= x2_roi and y1_roi <= cy <= y2_roi:
                    roi_boxes.append([x1, y1, x2, y2])
                    vehicle_info_map.append((cls_name, conf))
            
            if not roi_boxes:
                continue
            
            tracked = tracker.update(roi_boxes)
            
            if roi_id not in self.detected_vehicles:
                self.detected_vehicles[roi_id] = {}
            
            for i, (x3, y3, x4, y4, vehicle_id) in enumerate(tracked):
                cx, cy = (int(x3 + x4) // 2, int(y3 + y4) // 2)
                
                if i < len(vehicle_info_map):
                    cls_name, conf = vehicle_info_map[i]
                else:
                    cls_name = "vehicle"
                    conf = 0.0
                
                cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 0), 1)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                
                conf_percent = int(conf * 100)
                label = f"ID:{vehicle_id} {cls_name} {conf_percent}%"
                cv2.putText(frame, label, (x3, y3 - 10), 
                           cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 1)
                
                if vehicle_id not in self.detected_vehicles[roi_id]:
                    self.detected_vehicles[roi_id][vehicle_id] = {
                        'id': vehicle_id,
                        'type': cls_name,
                        'count': 0
                    }
                
                self.detected_vehicles[roi_id][vehicle_id]['count'] += 1
                
                if vehicle_id not in saved_ids:
                    car_img = frame[y3:y4, x3:x4]
                    if car_img.size != 0:
                        cv2.imwrite(f"{self.save_dir}/roi{roi_id}_car_{vehicle_id}.jpg", car_img)
                        saved_ids.add(vehicle_id)
        
        return frame
    
    def get_vehicle_list(self):
        """Lấy danh sách vehicles để hiển thị"""
        vehicle_list = []
        for roi_id, vehicles in self.detected_vehicles.items():
            for vehicle_id, info in vehicles.items():
                item_text = f"ROI{roi_id} - ID {vehicle_id}: {info['type']} (Count: {info['count']})"
                vehicle_list.append(item_text)
        return vehicle_list
    
    def reset_roi_vehicles(self, roi_id):
        """Reset vehicles của ROI"""
        if roi_id in self.detected_vehicles:
            del self.detected_vehicles[roi_id]
    
    def reset_all(self):
        """Reset tất cả vehicles"""
        self.detected_vehicles = {}

