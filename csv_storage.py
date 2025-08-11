import cv2
import csv


def open_csv_for_detections(output_folder=None, filename="detections_raw.csv"):
    path = (output_folder or '.') + "/" + filename
    csvfile = open(path, mode='w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(['id', 'Anomalie', 'confiance', 'frame', 'path_image'])
    return csvfile, writer, path

def write_detection(writer, id_local, nom_class, confiance, frame_idx, path_image=""):
    writer.writerow([id_local, nom_class, confiance, frame_idx, path_image])

def filter(input_csv_path, output_csv_path):
    best_detections = {}

    with open(input_csv_path, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            id_local = int(row['id'])
            nom_class = row['Anomalie']
            confiance = float(row['confiance'])

            # Clé = (id_local, nom_class) pour filtrer par couple
            key = (id_local, nom_class)

            if key not in best_detections or confiance > best_detections[key]['confiance']:
                best_detections[key] = {
                    'id': id_local,
                    'Anomalie': nom_class,
                    'confiance': confiance,
                    'frame': row['frame'],
                    'path_image': row.get('path_image', "")
                }

    with open(output_csv_path, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['id', 'Anomalie', 'confiance', 'frame', 'path_image'])
        for data in best_detections.values():
            writer.writerow([
                data['id'],
                data['Anomalie'],
                data['confiance'],
                data['frame'],
                data['path_image']
            ])