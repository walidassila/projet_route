import cv2
from tqdm import tqdm
from video_utils import open_video
from bounding_boxes import draw_boxes
import ultralytics

def trait_video(model,input_path,output_path,conf=0.4,class_colors=None):
    cap, fps, width, height, frame_count=open_video(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec MP4
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for _ in tqdm(range(frame_count), desc="📦 Traitement", unit="frame"):
        ret, frame = cap.read()
        if not ret:
            break
        results=model.predict(frame,imgsz=640,conf=conf,verbose=False)[0]
        draw_boxes(frame,results,class_colors)
        out.write(frame)
    
    cap.release()
    out.release()
    print("✅ Traitement terminé, vidéo sauvegardée dans :", output_path)