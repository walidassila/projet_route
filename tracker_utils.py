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
    if results.boxes is None or len(results.boxes) == 0:
        return np.empty((0,6), dtype=np.float32)  # si tu veux aussi class_id (mettre 0)

    boxes = results.boxes.xyxy.cpu().numpy()   # (N,4)
    scores = results.boxes.conf.cpu().numpy()  # (N,)
    classes = results.boxes.cls.cpu().numpy()  # (N,)

    # Concaténer x1,y1,x2,y2,score,class_id
    output = np.hstack((boxes, scores.reshape(-1,1), classes.reshape(-1,1)))
    return output.astype(np.float32)

    