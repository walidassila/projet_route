import cv2

def draw_boxes(frame, results, class_names=None,class_colors=None):
    for box in results.boxes:    
        cls_id = int(box.cls[0])
        cls_name = results.names[cls_id]
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        color = class_colors.get(cls_id, (255, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f'{class_names[cls_id]} {conf:.2f}'
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def draw_tracks(frame, online_targets, new_names, new_colors, id_map, counters):
    # Récupérer la liste des IDs actifs (old_id, cls)
    active_ids = set((track.track_id, track.cls) for track in online_targets)

    # Nettoyer id_map : ne garder que les actifs
    keys_to_keep = active_ids
    id_map = {k: v for k, v in id_map.items() if k in keys_to_keep}

    # Ajouter les nouveaux IDs jamais vus
    for key in active_ids:
        if key not in id_map:
            cls = key[1]
            if cls not in counters:
                counters[cls] = 1
            id_map[key] = counters[cls]
            counters[cls] += 1

    # Dessiner les boxes avec les IDs mis à jour
    for track in online_targets:
        old_id = track.track_id
        cls = track.cls
        new_id = id_map[(old_id, cls)]

        x1, y1, x2, y2 = map(int, track.tlbr)
        color = new_colors.get(cls, (0, 255, 0))
        class_name = new_names.get(cls, 'Unknown')

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f'ID:{new_id} {class_name}'
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return id_map, counters

