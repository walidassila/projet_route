from tracker_utils import create_tracker
tracker={"track_thresh":0.4, "track_buffer":30, "match_thresh":0.8, "min_box_area":10, "mot20":False}
print(create_tracker(**tracker))