import cv2
from tqdm import tqdm
from video_utils import prepare_video
from bounding_boxes import draw_boxes
import ultralytics
import os



def trait_video(model,input_path,output_folder=None,conf=0.4,class_colors=None):
    if output_folder is None:
        output_folder=os.getcwd()
    
    cap,frame_count,video_out,output_path=prepare_video(input_path, output_folder, fourcc_code='mp4v')
    
    for _ in tqdm(range(frame_count), desc="📦 Traitement", unit="frame"):
        ret, frame = cap.read()
        if not ret:
            break
        results=model.predict(frame,imgsz=640,conf=conf,verbose=False)[0]
        draw_boxes(frame,results,class_colors)
        video_out.write(frame)
    
    cap.release()
    video_out.release()
    print("✅ Traitement terminé, vidéo sauvegardée dans :", output_path)