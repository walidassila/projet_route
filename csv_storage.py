import cv2
import csv


def open_csv_for_detections(output_folder=None, filename="detections_raw.csv"):
    path = (output_folder or '.') + "/" + filename
    csvfile = open(path, mode='w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(['id_class', 'nom_class', 'frame_idx', 'id_local', 'confiance'])
    return csvfile, writer, path

def write_detection(writer, id_class, nom_class, frame_idx, id_local, confiance):
    writer.writerow([id_class, nom_class, frame_idx, id_local, confiance])

def filter_max_conf_per_idlocal(input_csv_path, output_csv_path):
    # Lecture et stockage du max confiance par id_local
    best_detections = {}

    with open(input_csv_path, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            id_local = int(row['id_local'])
            confiance = float(row['confiance'])
            # Si id_local pas encore vu ou confiance plus haute, on garde
            if id_local not in best_detections or confiance > best_detections[id_local]['confiance']:
                best_detections[id_local] = {
                    'id_class': row['id_class'],
                    'nom_class': row['nom_class'],
                    'frame_idx': row['frame_idx'],
                    'confiance': confiance
                }

    # Écriture du fichier filtré
    with open(output_csv_path, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['id_class', 'nom_class', 'frame_idx', 'id_local', 'confiance'])
        for id_local, data in best_detections.items():
            writer.writerow([
                data['id_class'],
                data['nom_class'],
                data['frame_idx'],
                id_local,
                data['confiance']
            ])