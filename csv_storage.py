import cv2
import csv


def open_csv_for_detections(output_folder=None, filename="detections_raw.csv"):
    import csv, os
    path = os.path.join(output_folder or '.', filename)
    csvfile = open(path, mode='w', newline='', encoding="utf-8")
    writer = csv.writer(csvfile)
    writer.writerow([
        "id_class", # ID de la classe localisée
        "Annomalie", # Nom réel de la classe (model.names)     
        "id_affichage",  # ID local
            
        "boundingbox",   # x1,y1,x2,y2
        "frame",         # Index précis de la frame
        "confiance",     # Score de confiance
        "image_path"     # Vide pour l’instant
    ])
    return csvfile, writer, path




def write_detection(writer, id_class, annomalie, id_affichage, bbox_coords, frame_idx, confiance, image_path=""):

    bbox_str = f"{bbox_coords[0]},{bbox_coords[1]},{bbox_coords[2]},{bbox_coords[3]}"
    writer.writerow([
        id_class,         # ID classe
        annomalie,        # Nom réel de la classe
        id_affichage,     # ID local
        bbox_str,         # Bounding box au format "x1,y1,x2,y2"
        frame_idx,        # Numéro de frame
        round(confiance, 4), # Confiance arrondie à 4 décimales
        image_path        # Chemin image (vide)
    ])

import csv

def filtering(input_csv_path, output_csv_path):
    best_detections = {}

    with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            id_class = int(row['id_class'])
            annomalie = row['Annomalie']
            id_affichage = int(row['id_affichage'])
            confiance = float(row['confiance'])
            bbox_str = row['boundingbox']
            frame_idx = int(row['frame'])
            image_path = row.get('image_path', "")

            # On filtre par (id_class, id_affichage)
            key = (id_class, id_affichage)

            # Garder uniquement la détection avec la plus forte confiance
            if key not in best_detections or confiance > best_detections[key]['confiance']:
                best_detections[key] = {
                    'id_class': id_class,
                    'Annomalie': annomalie,
                    'id_affichage': id_affichage,
                    'boundingbox': bbox_str,
                    'frame': frame_idx,
                    'confiance': confiance,
                    'image_path': image_path
                }

    # Écriture du CSV filtré
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['id_class', 'Annomalie', 'id_affichage', 'boundingbox', 'frame', 'confiance', 'image_path']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in best_detections.values():
            writer.writerow(data)

import os
import cv2
import csv
import zipfile
from pathlib import Path

import os
import csv
import cv2
import zipfile

def process_and_annotate_filtered_csv(
    input_csv_path, video_path, output_folder, new_colors
):
    # Créer dossier parent
    os.makedirs(output_folder, exist_ok=True)

    # Lire tout CSV
    with open(input_csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Extraire anomalies distinctes pour créer dossier
    anomalies = set(row['Annomalie'] for row in rows)
    anomaly_dirs = {}
    for anom in anomalies:
        path_dir = os.path.join(output_folder, anom)
        os.makedirs(path_dir, exist_ok=True)
        anomaly_dirs[anom] = path_dir

    # Ouvrir vidéo
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Impossible d'ouvrir la vidéo {video_path}")

    # Préparer CSV sortie
    output_csv_path = os.path.join(output_folder, 'filtered_with_paths.csv')
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as out_csv:
        fieldnames = ['id_class', 'Annomalie', 'id_affichage', 'boundingbox', 'frame', 'confiance', 'image_path']
        writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            frame_idx = int(row['frame'])
            anom = row['Annomalie']
            bbox_str = row['boundingbox']  # "x1,y1,x2,y2"
            id_class = row['id_class']
            id_affichage = row['id_affichage']
            confiance = row['confiance']

            # Lire frame demandée
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame_img = cap.read()
            if not ret:
                # Frame non trouvée, passer silencieusement
                continue

            # Dessiner bbox de la ligne seulement
            x1, y1, x2, y2 = map(int, bbox_str.split(','))
            color = new_colors.get(int(id_class), (0, 255, 0))
            cv2.rectangle(frame_img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame_img, anom, (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Sauvegarder image annotée dans dossier anomalie
            img_filename = f"frame{frame_idx}_id{id_affichage}.jpg"
            img_path = os.path.join(anomaly_dirs[anom], img_filename)
            cv2.imwrite(img_path, frame_img)

            # Écrire ligne CSV mise à jour avec path
            writer.writerow({
                'id_class': id_class,
                'Annomalie': anom,
                'id_affichage': id_affichage,
                'boundingbox': bbox_str,
                'frame': frame_idx,
                'confiance': confiance,
                'image_path': img_path
            })

    cap.release()

    # Zipper dossier parent
    zip_path = os.path.join(output_folder, "annotated_frames.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file == "annotated_frames.zip" or file == os.path.basename(output_csv_path):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_folder)
                zipf.write(file_path, arcname)

    # Silence total, pas de print
    return output_csv_path, zip_path
