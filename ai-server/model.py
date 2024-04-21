#!/usr/bin/env python3

import torchvision
import random

import torch
from torch import nn
from torchvision.models import vit_b_16
from huggingface_hub import hf_hub_download
import torchvision.transforms.functional
from ultralytics import YOLO
from supervision import Detections
import random
from torch.nn.functional import sigmoid
from torchvision.transforms.functional import normalize

model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt", cache_dir='/scratch/hina/clip-cache')
face_detection_model = YOLO(model_path, verbose=False).cpu()
model_path = 'model.pth'
drowsieness_detection_model = vit_b_16(num_classes=1)
drowsieness_detection_model.load_state_dict(torch.load(model_path))
drowsieness_detection_model = drowsieness_detection_model.cuda()
drowsieness_detection_model.eval()

preprocessor = torchvision.transforms.Compose([
    torchvision.transforms.Resize((224, 224)),
    torchvision.transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])

def detect_face(frame, leaway=(10,50)):
    x_offset1 = random.randint(*leaway)
    y_offset1 = random.randint(*leaway)
    x_offset2 = random.randint(*leaway)
    y_offset2 = random.randint(*leaway)
    result = Detections.from_ultralytics(face_detection_model(frame, verbose=False)[0]).xyxy
    if not len(result):
        print('No face detected')
        x1, y1, x2, y2 = 0, 0, frame.width, frame.height
        return frame, (x1, y1, x2, y2)
    x1, y1, x2, y2 = result[0]
    x1 = max(0, round(x1) - x_offset1)
    y1 = max(0, round(y1) - y_offset1)
    x2 = round(x2) + x_offset2
    y2 = round(y2) + y_offset2
    return None, (x1, y1, x2, y2)

@torch.no_grad()
def main():
    # just put everything in a loop
    while True:
        filename = input()
        vframes, _, _ = torchvision.io.read_video(filename)
        # convert to pil image
        vframes = vframes.permute(0, 3, 1, 2)
        f0 = torchvision.transforms.ToPILImage()(vframes[0])
        f0, (x1, y1, x2, y2) = detect_face(f0)
        vframes = vframes[:200, :, y1:y2, x1:x2].float() / 255.
        vframes = preprocessor(vframes)

        if x1 == 0 and y1 == 0 and x2 == f0.width and y2 == f0.height:
            continue
        
        # # TODO: The actual model call
        output = drowsieness_detection_model(vframes.cuda())
        output = sigmoid(output).mean()
        print(int(10 * output.item()))

        # print(f"Got tensor with shape {vframes.shape}")

if __name__ == "__main__":
    main()
