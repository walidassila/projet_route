import cv2
import csv
import os
import sqlite3
import shutil
import zipfile
from collections import defaultdict
import logging

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
        (id_class, anomalie, id_affichage, boundingbox, frame, confiance),
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
    SELECT *
    FROM (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY id_affichage, id_class ORDER BY confiance DESC, id ASC) AS rn
        FROM detections
    ) sub
    WHERE rn = 1;
    ''')
    
    conn.commit()
    
    # Supprimer les données brutes 
    cursor.execute('DROP TABLE detections')
    conn.commit()





def export_detections_as_images(conn, cursor, cap, output_folder, new_colors, video_path=None):
    import logging

    if video_path:
        video_name = os.path.splitext(os.path.basename(video_path))[0]
    else:
        video_name = "video"

    # Construire dossier base avec nom vidéo
    base_output = os.path.join(output_folder or os.getcwd(), f"detections_images_{video_name}")
    os.makedirs(base_output, exist_ok=True)

    # 1. Créer dossiers pour chaque anomalie
    cursor.execute("SELECT DISTINCT Anomalie FROM filtered_detections")
    anomalies = [row[0] for row in cursor.fetchall()]
    anomaly_dirs = {}
    for anomaly in anomalies:
        safe_name = anomaly.replace(" ", "_").replace("/", "_")
        path = os.path.join(base_output, safe_name)
        os.makedirs(path, exist_ok=True)
        anomaly_dirs[anomaly] = path

    # 2. Récupérer les détections triées
    cursor.execute("""
        SELECT id, id_class, Anomalie, id_affichage, boundingbox, frame, confiance, image_path
        FROM filtered_detections
        ORDER BY frame ASC
    """)
    rows = cursor.fetchall()

    detections_by_frame = defaultdict(list)
    for row in rows:
        detections_by_frame[row[5]].append(row)

    # 3. Chargement et annotation des frames
    conn_isolation = False
    try:
        conn_isolation = conn.isolation_level
        conn.isolation_level = None
    except Exception:
        pass

    try:
        for frame_num in sorted(detections_by_frame.keys()):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if not ret:
                logging.warning(f"Impossible de lire la frame {frame_num}")
                continue

            for detection in detections_by_frame[frame_num]:
                det_id, id_class, anomaly, id_affichage, bbox_str, frame_idx, conf, img_path = detection
                color = new_colors.get(id_class, (0, 255, 0))
                x1, y1, x2, y2 = map(int, bbox_str.split(","))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{anomaly} #{id_affichage}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            anomalies_in_frame = set(d[2] for d in detections_by_frame[frame_num])
            for anomaly in anomalies_in_frame:
                save_dir = anomaly_dirs[anomaly]
                filename = f"frame_{frame_num}.jpg"
                save_path = os.path.join(save_dir, filename)
                cv2.imwrite(save_path, frame)

                # Calcul du chemin relatif à partir du dossier PARENT de base_output
                parent_dir = os.path.dirname(base_output)
                rel_save_path = os.path.relpath(save_path, start=parent_dir)

                ids_to_update = [d[0] for d in detections_by_frame[frame_num] if d[2] == anomaly]
                cursor.executemany(
                    "UPDATE filtered_detections SET image_path = ? WHERE id = ?",
                    [(rel_save_path, det_id) for det_id in ids_to_update]
                )

        conn.commit()
    finally:
        if conn_isolation is not False:
            conn.isolation_level = conn_isolation

    # 4. Création archive ZIP
    zip_path = base_output + ".zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(base_output):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, base_output)
                zipf.write(full_path, arcname)

    # 5. Suppression dossier temporaire
    shutil.rmtree(base_output)

    return zip_path




def export_filtered_db_to_csv_and_cleanup(conn, cursor, db_path, output_folder, video_path):
 

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    csv_path = os.path.join(output_folder or os.getcwd(), f"detections_filtered_{base_name}.csv")

    # Sélectionner uniquement les colonnes voulues
    cursor.execute('''
        SELECT id_class, Anomalie, id_affichage, boundingbox, frame, confiance, image_path
        FROM filtered_detections
    ''')
    rows = cursor.fetchall()

    # Définir explicitement les noms des colonnes à écrire
    col_names = ['id_class', 'Anomalie', 'id_affichage', 'boundingbox', 'frame', 'confiance', 'image_path']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        writer.writerows(rows)

    # Fermer et supprimer la base SQLite
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

    return csv_path








