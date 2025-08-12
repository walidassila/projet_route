import os

input_path = r"C:\Users\walid\Desktop\vedeo_test.aoa.as"
base_name = os.path.splitext(os.path.basename(input_path))[0]
print(base_name)