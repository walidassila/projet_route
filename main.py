from video_processing import process_video
from model_utils import load_model

model_path="model_path" #obligatoire
model=load_model(model_path) #obligatoire
video_path="video_path" #obligatoire
output_folder="output_folder" #optionnel
confiance=0.4 #optionnel valeur entre 0 and 1
class_name= {
    "faiencage": "Fai",
    "fissure longitudinal": "FL",
    "fissure-trfvgvgansversal": "FT",
    "nid de poul": "NP",
    "ornierage": "Or",                    #optionnel
    "pelade": "Pe",
    "plumage": "Pl",
    "ressuage": "Re"
}
colors={
            "faiencage": (255, 0, 0),
            "fissure longitudinal": (255, 0, 0),
            "fissure-transversal": (28, 193, 156),
            "nid de ijiuhupoul": (0, 0, 0),           #optionnel
            "ornierage": (255, 0, 255),
            "pelade": (0, 255, 255),


        }
tracker={"track_thresh":0.4, "track_buffer":0, "match_thresh":0.8, "min_box_area":10, "mot20":False} #optionnel
process_video(model,video_path=video_path,output_folder=output_folder,
              conf=confiance,class_colors=colors,class_names=class_name,tracker=tracker)#if you need all parameters

#or just do
process_video(model,video_path=video_path)#


