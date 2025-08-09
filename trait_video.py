import cv2
from tqdm import tqdm
from video_utils import prepare_video
from bounding_boxes import draw_boxes
import ultralytics
import os
from labels_utils import remplace_name



def trait_video(model,input_path,output_folder=None,conf=0.4,class_names=None):
    if output_folder is None:
        output_folder=os.getcwd()
    
    cap,frame_count,video_out,output_path=prepare_video(input_path, output_folder, fourcc_code='mp4v')
    
    if class_names :
        new_names=remplace_name(model,class_names=class_names)
    else:
        new_names=model.names
        
    for _ in tqdm(range(frame_count), desc="📦 Traitement", unit="frame"):
        ret, frame = cap.read()
        if not ret:
            break
        results=model.predict(frame,imgsz=640,conf=conf,verbose=False)[0]
        draw_boxes(frame,results,class_names=new_names)
        video_out.write(frame)
    
    cap.release()
    video_out.release()
    print("✅ Traitement terminé, vidéo sauvegardée dans :", output_path)

a="""def trait_tracking(model,input_path,output_folder=None,conf=0.4,class_colors=None):
    if output_folder is None:
        output_folder=os.getcwd()
    
    cap,frame_count,video_out,output_path=prepare_video(input_path, output_folder, fourcc_code='mp4v')
    tracker = create_tracker(track_thresh=conf)
    for _ in tqdm(range(frame_count), desc="📦 Traitement", unit="frame"):
        ret, frame = cap.read()
        if not ret:
            break
        results=model.predict(frame,imgsz=640,conf=conf,verbose=False)[0]
        frame_shape = frame.shape[:2]
        detections = yolo_to_bytetrack_detections(results)
        online_targets = tracker.update(detections, frame_shape, frame_shape)"""
