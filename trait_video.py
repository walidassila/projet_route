import cv2
from tqdm import tqdm
from data_storage import open_db_for_detections,insert_detections_batch,filter_detections_keep_max_conf,export_detections_as_images,export_filtered_db_to_csv_and_cleanup
from video_utils import prepare_video_processing
from bounding_boxes import draw_boxes,draw_tracks
import ultralytics
import os
from labels_utils import replace_name,replace_color
from tracker_utils import create_tracker
from tracker_utils import yolo_to_bytetrack_detections
from id_local_manager import IDLocalManagerFast
import numpy as np
import math
import csv

np.float = float




def trait_video(model,video_path,output_folder=None,conf=0.4,class_names=None,class_colors=None):
    cap, frame_count, video_out, output_path, new_names, new_colors=prepare_video_processing(model,video_path,output_folder=output_folder,class_names=class_names,class_colors=class_colors)
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

def trait_tracking(model, video_path, output_folder=None, conf=0.4,
                   class_names=None, class_colors=None, tracker=None):

    cap, frame_count, video_out, output_path, new_names, new_colors = prepare_video_processing(
        model, video_path, output_folder=output_folder,
        class_names=class_names, class_colors=class_colors
    )

    tracker = create_tracker(tracker=tracker)
    id_manager = IDLocalManagerFast()


    conn, cursor, db_path = open_db_for_detections(output_folder)
    batch_inserts = []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    for frame_idx in tqdm(range(frame_count), desc="📦 Traitement", unit="frame"):
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, imgsz=640, conf=conf, verbose=False)[0]
        frame_shape = frame.shape[:2]

        detections = yolo_to_bytetrack_detections(results)
        online_targets = tracker.update(detections, frame_shape, frame_shape)

        id_manager.update_removed(tracker.removed_stracks)

        frame_int = int(frame_idx)

        for track in online_targets:
            bbox = track.tlbr
            track_id = track.track_id
            class_id = int(track.class_id)
            conf_score = round(float(track.score if hasattr(track, 'score') else 0.0), 2)

            local_id = id_manager.get_or_add(track_id, class_id)
            class_name = new_names.get(class_id, 'Unknown')
            color = new_colors.get(class_id, (0, 255, 0))
            x1, y1, x2, y2 = map(int, bbox)
            bbox_str = f"{x1},{y1},{x2},{y2}"
            
            batch_inserts.append((
                class_id,
                model.names[class_id],
                local_id,
                bbox_str,
                frame_int,
                conf_score
            ))
            

            # Dessiner sur la frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f'#id:{local_id} {class_name}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        video_out.write(frame)
        if len(batch_inserts) >= 100:
            insert_detections_batch(cursor, batch_inserts)
            conn.commit()
            batch_inserts.clear()

    
        # Insérer le reste des détections
    if batch_inserts:
        insert_detections_batch(cursor, batch_inserts)
        conn.commit()
        batch_inserts.clear()
    
    video_out.release()
    

    # Filtrer les détections dans la base pour garder max confiance par id_affichage/id_class
    filter_detections_keep_max_conf(conn, cursor)
    zip_path = export_detections_as_images(conn, cursor, cap, output_folder, new_colors, video_path)
    cap.release()  # release après le traitement final
    csv_path = export_filtered_db_to_csv_and_cleanup(conn, cursor, db_path, output_folder, video_path)
    
    print(f"Vidéo sortie enregistrée ici : {output_path}")
    print(f"Archive ZIP créée ici : {zip_path}")
    print(f"Fichier CSV exporté ici : {csv_path}")
    
    
