# load libraries
from huggingface_hub import hf_hub_download
from ultralytics import YOLO
from supervision import Detections
from PIL import Image
import random

model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt", cache_dir='/scratch/hina/clip-cache')
# load model
face_detection_model = YOLO(model_path, verbose=False).cpu()

def detect_face(frame, leaway=(10,50)):
    x_offset1 = random.randint(*leaway)
    y_offset1 = random.randint(*leaway)
    x_offset2 = random.randint(*leaway)
    y_offset2 = random.randint(*leaway)
    result = Detections.from_ultralytics(face_detection_model(frame, verbose=False)[0]).xyxy
    if not len(result):
        print('No face detected')
        x1, y1, x2, y2 = 0, 0, frame.shape[1], frame.shape[0]
        return frame, (x1, y1, x2, y2)
    x1, y1, x2, y2 = result[0]
    x1 = max(0, round(x1) - x_offset1)
    y1 = max(0, round(y1) - y_offset1)
    x2 = round(x2) + x_offset2
    y2 = round(y2) + y_offset2

    if (x2-x1) < 40 or (y2-y1) < 40:
        print('Face too small')
        x1, y1, x2, y2 = 0, 0, frame.shape[1], frame.shape[0]
        return frame, (x1, y1, x2, y2)
    return frame[y1:y2, x1:x2], (x1, y1, x2, y2)

