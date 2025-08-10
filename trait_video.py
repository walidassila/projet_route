import cv2
from tqdm import tqdm
from video_utils import prepare_video
from bounding_boxes import draw_boxes,draw_tracks
import ultralytics
import os
from labels_utils import remplace_name,replace_color
from tracker_utils import create_tracker
from tracker_utils import yolo_to_bytetrack_detections
import numpy as np
np.float = float

def prepare_video_processing(model,input_path, output_folder=None, class_names=None, class_colors=None):
    """
    Prépare les objets nécessaires pour traiter une vidéo :
    - crée output_folder s'il n'existe pas,
    - prépare la vidéo (capture, frame count, writer, output path),
    - remplace les noms des classes si class_names fourni,
    - remplace ou initialise les couleurs des classes.

    Retourne : cap, frame_count, video_out, output_path, new_names, class_colors
    """
    if output_folder is None:
        output_folder = os.getcwd()
    
    # Prépare la vidéo (cette fonction doit exister dans ton code)
    cap, frame_count, video_out, output_path = prepare_video(input_path, output_folder, fourcc_code='mp4v')
    
    # Gère les noms des classes
    if class_names:
        new_names = remplace_name(model, class_names=class_names)
    else:
        new_names = model.names
    
    # Gère les couleurs des classes
    class_colors = replace_color(model, class_colors=class_colors)
    
    return cap, frame_count, video_out, output_path, new_names, class_colors

def trait_video(model,input_path,output_folder=None,conf=0.4,class_names=None,class_colors=None):
    cap, frame_count, video_out, output_path, new_names, new_colors=prepare_video_processing(model,input_path,output_folder=output_folder,class_names=class_names,class_colors=class_colors)
    for _ in tqdm(range(frame_count), desc="📦 Traitement", unit="frame"):
        ret, frame = cap.read()
        if not ret:
            break
        results=model.predict(frame,imgsz=640,conf=conf,verbose=False)[0]
        draw_boxes(frame,results,class_names=new_names,class_colors=new_colors)
        video_out.write(frame)
    
    cap.release()
    video_out.release()
    print("✅ Traitement terminé, vidéo sauvegardée dans :", output_path)


#fichier trait_vedeo.py
def trait_tracking(model,input_path,output_folder=None,conf=0.4,class_names=None,class_colors=None,tracker=None):
    id_map = {}
    counters = {}
    cap, frame_count, video_out, output_path, new_names, new_colors=prepare_video_processing(model,input_path,output_folder=output_folder,class_names=class_names,class_colors=class_colors)
    tracker = create_tracker(tracker=tracker)
    for _ in tqdm(range(frame_count), desc="📦 Traitement", unit="frame"):
        ret, frame = cap.read()
        if not ret:
            break
        results=model.predict(frame,imgsz=640,conf=conf,verbose=False)[0]
        frame_shape = frame.shape[:2]
        detections = yolo_to_bytetrack_detections(results)
        online_targets = tracker.update(detections, frame_shape, frame_shape)
        
        for i, track in enumerate(online_targets):
            if i < len(detections):
                track.cls = int(detections[i, 5].item())  # detections est un tensor (x1,y1,x2,y2,score,cls)
            else:
                track.cls = -1  # ou None, si on a plus de tracks que détections
        
        id_map, counters = draw_tracks(frame, online_targets, new_names, new_colors, id_map, counters)
        video_out.write(frame)
    
    video_out.release()
    cap.release()
