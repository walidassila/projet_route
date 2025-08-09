import cv2
from labels_utils import Labels

def draw_boxes(frame, results, class_names):
    l=Labels()
    for box in results.boxes:    
        cls_id = int(box.cls[0])
        cls_name = results.names[cls_id]
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        color = l.class_colors.get(cls_name, (255, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f'{class_names[cls_id]} {conf:.2f}'
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
