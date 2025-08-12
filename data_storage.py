import cv2
import csv
import os
import sqlite3

def open_db_for_detections(output_folder):
    db_path = os.path.join(output_folder or '.', "detections.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Table brute
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_class INTEGER,
            Anomalie TEXT,  -- normalisé à un seul "n"
            id_affichage INTEGER,
            boundingbox TEXT,
            frame INTEGER,
            confiance REAL,
            image_path TEXT DEFAULT ''
        )
    ''')
    
    # Index pour accélérer la recherche du max
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_affichage_class_conf 
        ON detections(id_affichage, id_class, confiance)
    ''')
    
    conn.commit()
    return conn, cursor, db_path

def insert_detections_batch(cursor, detections_list):
    """
    detections_list = [
        (id_class, annomalie, id_affichage, boundingbox, frame, confiance),
        ...
    ]
    """
    cursor.executemany('''
        INSERT INTO detections (id_class, Anomalie, id_affichage, boundingbox, frame, confiance)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', detections_list)


def filter_detections_keep_max_conf(conn, cursor):
    # Crée la table filtrée à partir des données brutes
    cursor.execute('DROP TABLE IF EXISTS filtered_detections')
    cursor.execute('''
        CREATE TABLE filtered_detections AS
        SELECT d1.*
        FROM detections d1
        INNER JOIN (
            SELECT id_affichage, id_class, MAX(confiance) AS max_conf
            FROM detections
            GROUP BY id_affichage, id_class
        ) d2
        ON d1.id_affichage = d2.id_affichage 
           AND d1.id_class = d2.id_class 
           AND d1.confiance = d2.max_conf
    ''')
    
    conn.commit()
    
    # Supprimer les données brutes 
    cursor.execute('DROP TABLE detections')
    conn.commit()









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
