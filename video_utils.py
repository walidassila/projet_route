import cv2
import os
from labels_utils import replace_name,replace_color

def get_video_info(input_video_path):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise IOError(f"Impossible d'ouvrir la vidéo : {input_video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    return cap, fps, width, height, frame_count


def prepare_video(input_path, output_folder, fourcc_code='mp4v'):
    video_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_folder, f"{video_name}_processed.mp4")
    cap, fps, width, height, frame_count=get_video_info(input_path)    
    fourcc = cv2.VideoWriter_fourcc(*fourcc_code)
    video_out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    return cap,frame_count,video_out,output_path

def prepare_video_processing(model,video_path, output_folder=None, class_names=None, class_colors=None):

    if output_folder is None:
        output_folder = os.getcwd()
    
    # Prépare la vidéo (cette fonction doit exister dans ton code)
    cap, frame_count, video_out, output_path = prepare_video(video_path, output_folder, fourcc_code='mp4v')
    
    # Gère les noms des classes
    if class_names:
        new_names = replace_name(model, class_names=class_names)
    else:
        new_names = model.names
    
    # Gère les couleurs des classes
    class_colors = replace_color(model, class_colors=class_colors)
    
    return cap, frame_count, video_out, output_path, new_names, class_colors
