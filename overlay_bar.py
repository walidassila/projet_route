from labels_utils import generate_abbreviation
import cv2
import numpy as np

def draw_realtime_bar(frame, current_counts, class_names, class_colors):
    """
    Affiche une barre dynamique avec compteurs en temps réel.
    - class_names : dict {class_id: class_name}
    - class_colors : dict {class_name: (B, G, R)}
    """
    height, width = frame.shape[:2]
    overlay = frame.copy()

    abbreviations = {
        cls_name: generate_abbreviation(cls_name, length=4)
        for cls_name in class_names.values()
    }

    margin_ratio = 0.015
    padding_ratio = 0.01
    line_height_ratio = 0.035
    box_width_ratio = 0.2
    cols = 2

    margin = max(10, min(30, int(width * margin_ratio)))
    padding = max(5, min(20, int(height * padding_ratio)))
    line_height = max(20, min(50, int(height * line_height_ratio)))
    box_width = max(100, min(300, int(width * box_width_ratio)))

    rows = (len(abbreviations) + 1) // cols
    box_height = rows * line_height + 2 * padding

    top_left_x = margin
    top_left_y = margin
    bottom_right_x = top_left_x + cols * box_width + (cols - 1) * margin
    bottom_right_y = top_left_y + box_height

    cv2.rectangle(overlay, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (30, 30, 30), -1)

    font_scale = max(0.4, min(1.2, height / 1080 * 0.8))
    font_thickness = max(1, min(3, int(height / 720)))
    rect_size = int(height * 0.025)

    for idx, (cls_name, abbrev) in enumerate(abbreviations.items()):
        count = current_counts.get(cls_name, 0)
        color = class_colors.get(cls_name, (255, 255, 255))

        col = idx % cols
        row = idx // cols

        x_rect = top_left_x + col * (box_width + margin)
        y_rect = top_left_y + padding + row * line_height

        square_top_left = (x_rect + 5, y_rect + (line_height - rect_size) // 2)
        square_bottom_right = (square_top_left[0] + rect_size, square_top_left[1] + rect_size)
        cv2.rectangle(overlay, square_top_left, square_bottom_right, color, -1)

        text = f"{abbrev}: {count}"
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
        text_x = square_bottom_right[0] + 10
        text_y = y_rect + (line_height + text_height) // 2 - 2

        cv2.putText(overlay, text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

    alpha = 0.75
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    return frame


def draw_final_animation(video_out, last_frame, class_counts_total, class_names, class_colors, fps, width, height):
    """
    Animation finale avec les totaux par classe.
    - class_names : dict {class_id: class_name}
    - class_colors : dict {class_name: (B, G, R)}
    """
    abbreviations = {
        cls_name: generate_abbreviation(cls_name, length=4)
        for cls_name in class_names.values()
    }

    margin = max(10, min(30, int(width * 0.015)))
    padding = max(5, min(20, int(height * 0.01)))
    line_height = max(20, min(50, int(height * 0.035)))
    box_width = max(100, min(300, int(width * 0.2)))
    cols = 2
    rows = (len(abbreviations) + 1) // cols
    box_height = rows * line_height + 2 * padding

    font_scale = max(0.4, min(1.2, height / 1080 * 0.8))
    font_thickness = max(1, min(3, int(height / 720)))
    rect_size = int(height * 0.025)
    alpha = 0.75

    move_duration_sec = 3
    static_duration_sec = 3
    num_frames_move = int(fps * move_duration_sec)
    num_frames_static = int(fps * static_duration_sec)
    num_frames_total = num_frames_move + num_frames_static

    for frame_idx in range(num_frames_total):
        anim_frame = last_frame.copy()
        overlay = anim_frame.copy()

        if frame_idx < num_frames_move:
            progress = frame_idx / num_frames_move
            eased_progress = 0.5 - 0.5 * np.cos(np.pi * progress)

            y_offset = int((height // 2 - box_height // 2 - margin) * eased_progress)
            top_left_y_anim = margin + y_offset
            bottom_right_y_anim = top_left_y_anim + box_height

            x_center = width // 2
            initial_x = margin
            target_x = x_center - (cols * box_width + (cols - 1) * margin) // 2
            x_offset = int((target_x - initial_x) * eased_progress)
            top_left_x_anim = initial_x + x_offset
            bottom_right_x_anim = top_left_x_anim + cols * box_width + (cols - 1) * margin
        else:
            top_left_y_anim = height // 2 - box_height // 2
            bottom_right_y_anim = top_left_y_anim + box_height
            top_left_x_anim = width // 2 - (cols * box_width + (cols - 1) * margin) // 2
            bottom_right_x_anim = top_left_x_anim + cols * box_width + (cols - 1) * margin

        cv2.rectangle(overlay, (top_left_x_anim, top_left_y_anim), (bottom_right_x_anim, bottom_right_y_anim), (30, 30, 30), -1)

        for idx, (cls_name, abbrev) in enumerate(abbreviations.items()):
            count = class_counts_total.get(cls_name, 0)
            color = class_colors.get(cls_name, (255, 255, 255))

            col = idx % cols
            row = idx // cols

            x_rect = top_left_x_anim + col * (box_width + margin)
            y_rect = top_left_y_anim + padding + row * line_height

            square_top_left = (x_rect + 5, y_rect + (line_height - rect_size) // 2)
            square_bottom_right = (square_top_left[0] + rect_size, square_top_left[1] + rect_size)
            cv2.rectangle(overlay, square_top_left, square_bottom_right, color, -1)

            text = f"{abbrev}: {count}"
            cv2.putText(overlay, text, (square_bottom_right[0] + 10, y_rect + (line_height + rect_size // 2)),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

        cv2.addWeighted(overlay, alpha, anim_frame, 1 - alpha, 0, anim_frame)
        video_out.write(anim_frame)