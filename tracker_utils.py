# tracker_utils.py
from yolox.tracker.byte_tracker import BYTETracker
from yolox.tracker.byte_tracker import STrack

class TrackerArgs:
    def __init__(self, track_thresh=0.4, track_buffer=30, match_thresh=0.8, min_box_area=10, mot20=False):
        self.track_thresh = track_thresh
        self.track_buffer = track_buffer
        self.match_thresh = match_thresh
        self.min_box_area = min_box_area
        self.mot20 = mot20

def create_tracker():
    args = TrackerArgs()
    return BYTETracker(args)
