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
