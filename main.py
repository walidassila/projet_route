import sqlite3
import csv
import os

def create_table_and_import_csv(csv_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Création table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_class INTEGER,
            Anomalie TEXT,
            id_affichage INTEGER,
            boundingbox TEXT,
            frame INTEGER,
            confiance REAL,
            image_path TEXT
        )
    ''')
    conn.commit()

    # Vider table si besoin
    cursor.execute('DELETE FROM detections')
    conn.commit()

    # Insérer le CSV ligne par ligne
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(row['id_class']),
                row['Anomalie'],
                int(row['id_affichage']),
                row['boundingbox'],
                int(row['frame']),
                float(row['confiance']),
                row.get('image_path', '')
            )
            for row in reader
        ]

    cursor.executemany('''
        INSERT INTO detections (id_class, Anomalie, id_affichage, boundingbox, frame, confiance, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', rows)
    conn.commit()

    return conn, cursor

def test_filter_query(cursor):
    cursor.execute('''
    SELECT *
    FROM (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY id_affichage, id_class ORDER BY confiance DESC, id ASC) as rn
        FROM detections
    ) sub
    WHERE rn = 1
    ''')
    rows = cursor.fetchall()
    print(f"Nombre de lignes filtrées : {len(rows)}")
    for r in rows[:5]:  # Affiche quelques lignes exemples
        print(r)

# Chemins à adapter
csv_path = r"C:\Users\walid\Downloads\detections_tri0.csv"
db_path = "test_detections.db"

conn, cursor = create_table_and_import_csv(csv_path, db_path)
test_filter_query(cursor)

conn.close()
os.remove(db_path)  # Nettoyage si tu veux
