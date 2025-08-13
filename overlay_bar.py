import cv2
import numpy as np
from collections import defaultdict

def draw_fixed_realtime_bar(frame, current_counts, class_colors, abbreviations, cols=2):

    height, width = frame.shape[:2]
    overlay = frame.copy()

    # Paramètres dynamiques
    margin = max(10, min(30, int(width * 0.015)))
    padding = max(5, min(20, int(height * 0.01)))
    line_height = max(20, min(50, int(height * 0.035)))
    box_width = max(100, min(300, int(width * 0.2)))

    rows = (len(abbreviations) + cols - 1) // cols
    box_height = rows * line_height + 2 * padding

    top_left_x = margin
    top_left_y = margin

    # Dessiner le fond du cadre
    bottom_right_x = top_left_x + cols * box_width + (cols - 1) * margin
    bottom_right_y = top_left_y + box_height
    cv2.rectangle(overlay, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (30, 30, 30), -1)

    # Texte et carrés couleur
    font_scale = max(0.4, min(1.2, height / 1080 * 0.8))
    font_thickness = max(1, min(3, int(height / 720)))
    rect_size = int(height * 0.025)

    for idx, cls_id in enumerate(abbreviations):
        abbr = abbreviations[cls_id]
        count = current_counts.get(cls_id, 0)
        color = class_colors.get(cls_id, (255, 255, 255))

        col = idx % cols
        row = idx // cols

        x_rect = top_left_x + col * (box_width + margin)
        y_rect = top_left_y + padding + row * line_height

        # Carré couleur
        square_top_left = (x_rect + 5, y_rect + (line_height - rect_size) // 2)
        square_bottom_right = (square_top_left[0] + rect_size, square_top_left[1] + rect_size)
        cv2.rectangle(overlay, square_top_left, square_bottom_right, color, -1)

        # Texte
        text = f"{abbr}: {count}"
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
        text_x = square_bottom_right[0] + 10
        text_y = y_rect + (line_height + text_height) // 2 - 2
        cv2.putText(overlay, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

    alpha = 0.75
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    return frame, (top_left_x, top_left_y)


def animate_final_bar_fixed(video_out, last_frame, conn, new_colors, abbreviations, fps, current_bar_pos, cols=2):
    """
    Anime la barre de la position actuelle vers le centre et affiche le résultat final pendant 5 secondes.
    """
    cursor = conn.cursor()
    # Totaux depuis la table filtrée
    cursor.execute("SELECT id_class, COUNT(*) FROM filtered_detections GROUP BY id_class")
    results = cursor.fetchall()
    total_counts = defaultdict(int, {row[0]: row[1] for row in results})

    h, w = last_frame.shape[:2]
    bar_width = max(100, min(300, int(w * 0.2))) * cols
    line_height = max(20, min(50, int(h * 0.035)))
    padding = max(5, min(20, int(h * 0.01)))
    rows = (len(abbreviations) + cols - 1) // cols
    box_height = rows * line_height + 2 * padding

    final_pos = np.array([w // 2 - bar_width // 2, h // 2 - box_height // 2], dtype=float)
    start_pos = np.array(current_bar_pos, dtype=float)

    # Animation 1 seconde
    anim_frames = int(fps)
    for step in range(1, anim_frames + 1):
        t = step / anim_frames
        interp_pos = (1 - t) * start_pos + t * final_pos
        frame = last_frame.copy()
        frame, _ = draw_fixed_realtime_bar(frame, total_counts, new_colors, abbreviations, cols=cols)
        x_offset, y_offset = int(interp_pos[0]), int(interp_pos[1])

        # Overlay partiel pour simuler le déplacement
        temp_frame = frame.copy()
        y_end = min(frame.shape[0], y_offset + temp_frame.shape[0])
        x_end = min(frame.shape[1], x_offset + temp_frame.shape[1])
        frame[y_offset:y_end, x_offset:x_end] = temp_frame[0:y_end - y_offset, 0:x_end - x_offset]

        video_out.write(frame)

    # Affichage fixe 5 secondes
    display_frames = 5 * fps
    for _ in range(display_frames):
        frame = last_frame.copy()
        frame, _ = draw_fixed_realtime_bar(frame, total_counts, new_colors, abbreviations, cols=cols)
        video_out.write(frame)