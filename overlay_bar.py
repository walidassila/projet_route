import cv2
import numpy as np
from collections import defaultdict

def draw_fixed_realtime_bar(frame, current_counts, class_colors, abbreviations, cols=2):
    height, width = frame.shape[:2]
    overlay = frame.copy()

    # Marges et padding proportionnels à la taille de la vidéo
    margin = max(10, int(width * 0.015))
    padding = max(5, int(height * 0.01))
    line_height = max(20, int(height * 0.035))
    box_width = max(100, min(int(width / 4), 300))  # ne dépasse pas 1/4 de la largeur

    rows = (len(abbreviations) + cols - 1) // cols
    box_height = rows * line_height + 2 * padding

    top_left_x = margin
    top_left_y = margin
    bottom_right_x = top_left_x + cols * box_width + (cols - 1) * margin
    bottom_right_y = top_left_y + box_height

    # Fond semi-transparent
    cv2.rectangle(overlay, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (30, 30, 30), -1)

    # Ajustement du texte et des rectangles en fonction de la résolution
    font_scale = max(0.3, min(1.2, height / 1080 * 0.7))
    font_thickness = max(1, min(3, int(height / 720)))
    rect_size = max(10, int(height * 0.025))

    for idx, cls_id in enumerate(abbreviations):
        abbr = abbreviations[cls_id]
        count = current_counts.get(cls_id, 0)
        color = class_colors.get(cls_id, (255, 255, 255))

        col = idx % cols
        row = idx // cols

        x_rect = top_left_x + col * (box_width + margin)
        y_rect = top_left_y + padding + row * line_height

        square_top_left = (x_rect + 5, y_rect + (line_height - rect_size) // 2)
        square_bottom_right = (square_top_left[0] + rect_size, square_top_left[1] + rect_size)
        cv2.rectangle(overlay, square_top_left, square_bottom_right, color, -1)

        text = f"{abbr}: {count}"
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
        text_x = square_bottom_right[0] + 10
        text_y = y_rect + (line_height + text_height) // 2 - 2
        cv2.putText(overlay, text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

    # Fusion semi-transparente
    alpha = 0.75
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    return frame




