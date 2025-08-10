from trait_video import trait_video,trait_tracking
from model_utils import load_model

model=load_model(r"C:\Users\walid\Desktop\stage_pfa\projet_models\projet_route_model_best_version_93%p-20250803T142319Z-1-001\projet_route_model_best_version_93_p\projet_route_model_best_version_93%pr_walid\run12\weights\best.pt")
input=r"C:\Users\walid\Desktop\vedeo_test\tri0.mp4"
output=r"C:\Users\walid\Desktop\re"
trait_tracking(model,input_path=input,output_folder=output,conf=0.1)