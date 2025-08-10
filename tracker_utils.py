# tracker_utils.py
from yolox.tracker.byte_tracker import BYTETracker
from yolox.tracker.byte_tracker import STrack
import torch
import numpy as np
np.float = float

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
#fichier tracker_utils.py
def yolo_to_bytetrack_detections(results):
    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        score = float(box.conf[0])
        cls = int(box.cls[0])
        detections.append([x1, y1, x2, y2, score, cls])
    
    if detections:
        # Retourne un tensor PyTorch (float32 par défaut)
        return torch.tensor(detections, dtype=torch.float32)
    else:
        return torch.empty((0, 6), dtype=torch.float32)

    