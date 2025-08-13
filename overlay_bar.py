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
    bottom_right_x = top_left_x + cols * box_width + (cols - 1) * margin
    bottom_right_y = top_left_y + box_height

    # Dessiner le fond du cadre
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

        cv2.putText(overlay, text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

    alpha = 0.75
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    return frame

def append_final_summary(video_out, cap, frame_count, fps, totals, class_colors, abbreviations, cols=2):
    """
    Ajoute à la vidéo 5 secondes avec la dernière frame comme background
    et la barre récapitulative des totaux par classe.
    """
    # Charger la dernière frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
    ret, last_frame = cap.read()
    if not ret:
        last_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    # Dessiner la barre finale avec draw_fixed_realtime_bar
    final_frame = draw_fixed_realtime_bar(last_frame.copy(), totals, class_colors, abbreviations, cols=cols)

    # Ajouter 5 secondes de cette frame
    for _ in range(int(fps * 5)):
        video_out.write(final_frame)
 

 #########
def animate_final_results(video_out, last_frame, fps, final_counts, class_colors, abbreviations, cols=2,
                          move_duration_sec=3, static_duration_sec=2):
    """
    Affiche la barre finale animée depuis le haut vers le centre
    avec la dernière frame comme background.
    """
    height, width = last_frame.shape[:2]

    # Paramètres dynamiques pour la barre
    margin = max(10, min(30, int(width * 0.015)))
    padding = max(5, min(20, int(height * 0.01)))
    line_height = max(20, min(50, int(height * 0.035)))
    box_width = max(100, min(300, int(width * 0.2)))
    rows = (len(abbreviations) + cols - 1) // cols
    box_height = rows * line_height + 2 * padding

    font_scale = max(0.4, min(1.2, height / 1080 * 0.8))
    font_thickness = max(1, min(3, int(height / 720)))
    rect_size = int(height * 0.025)
    alpha = 0.75

    num_frames_move = int(fps * move_duration_sec)
    num_frames_static = int(fps * static_duration_sec)
    num_frames_total = num_frames_move + num_frames_static

    for frame_idx in range(num_frames_total):
        frame = last_frame.copy()
        overlay = frame.copy()

        if frame_idx < num_frames_move:
            progress = frame_idx / num_frames_move
            eased_progress = 0.5 - 0.5 * np.cos(np.pi * progress)  # easing cosinus

            # Calcul position verticale et horizontale
            y_offset = int((height // 2 - box_height // 2 - margin) * eased_progress)
            top_left_y = margin + y_offset
            bottom_right_y = top_left_y + box_height

            x_center = width // 2
            initial_x = margin
            target_x = x_center - (cols * box_width + (cols - 1) * margin) // 2
            x_offset = int((target_x - initial_x) * eased_progress)
            top_left_x = initial_x + x_offset
            bottom_right_x = top_left_x + cols * box_width + (cols - 1) * margin
        else:
            top_left_y = height // 2 - box_height // 2
            bottom_right_y = top_left_y + box_height
            top_left_x = width // 2 - (cols * box_width + (cols - 1) * margin) // 2
            bottom_right_x = top_left_x + cols * box_width + (cols - 1) * margin

        # Fond du cadre
        cv2.rectangle(overlay, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (30, 30, 30), -1)

        # Dessin des carrés + texte
        for idx, cls in enumerate(abbreviations):
            abbr = abbreviations[cls]
            count = final_counts.get(cls, 0)
            color = class_colors.get(cls, (255, 255, 255))

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
            cv2.putText(overlay, text, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

        # Fusion overlay
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        video_out.write(frame)
