from collections import defaultdict
import math

class Tracker:
    def __init__(self, max_distance=40, max_history=40):
        self.track_history = defaultdict(lambda: [])
        
        self.id_count = 0
        
        # Khoảng cách tối đa để coi là cùng object
        self.max_distance = max_distance
        
        # Số điểm lịch sử tối đa lưu cho mỗi object
        self.max_history = max_history

    def update(self, objects_rect):
        """
        Cập nhật tracker với danh sách bounding box mới.
        objects_rect: [(x1, y1, x2, y2), ...]
        return: [(x1, y1, x2, y2, id), ...]
        """
        objects_bbs_ids = []

        # Duyệt từng bounding box
        for rect in objects_rect:
            x1, y1, x2, y2 = rect
            
            # Tính tâm bounding box
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            same_object_detected = False

            # So sánh với các object đã track trước đó
            for obj_id, track in self.track_history.items():
                prev_center = track[-1]  # Tâm trước đó
                dist = math.hypot(cx - prev_center[0], cy - prev_center[1])  # Khoảng cách Euclid
                
                # Nếu khoảng cách nhỏ hơn ngưỡng → cùng object
                if dist < self.max_distance:
                    self.track_history[obj_id].append((cx, cy))

                    # Giới hạn số điểm lịch sử
                    if len(self.track_history[obj_id]) > self.max_history:
                        self.track_history[obj_id].pop(0)

                    objects_bbs_ids.append([x1, y1, x2, y2, obj_id])
                    same_object_detected = True
                    break

            # Nếu không khớp với object nào → tạo ID mới
            if not same_object_detected:
                self.track_history[self.id_count].append((cx, cy))
                objects_bbs_ids.append([x1, y1, x2, y2, self.id_count])
                self.id_count += 1

        # Chỉ giữ lại lịch sử của các object còn xuất hiện
        new_track_history = defaultdict(lambda: [])
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            new_track_history[object_id] = self.track_history[object_id]

        self.track_history = new_track_history.copy()
        return objects_bbs_ids
