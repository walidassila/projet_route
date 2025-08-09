# tracker_utils.py
from yolox.tracker.byte_tracker import BYTETracker
from yolox.tracker.byte_tracker import STrack
import numpy as np

class TrackerArgs:
    def __init__(self, track_thresh=0.4, track_buffer=30, match_thresh=0.8, min_box_area=10, mot20=False):
        self.track_thresh = track_thresh
        self.track_buffer = track_buffer
        self.match_thresh = match_thresh
        self.min_box_area = min_box_area
        self.mot20 = mot20

def create_tracker(tracker=None):
    if tracker is None:
            tracker = {}
    args = TrackerArgs(**tracker)
    return BYTETracker(args)

def yolo_to_bytetrack_detections(results):
    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        score = float(box.conf[0])
        cls = int(box.cls[0])
        detections.append([x1, y1, x2, y2, score, cls])
    
    if detections:
        return np.array(detections)
    else:
        return np.empty((0, 6))

    