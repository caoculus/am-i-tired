from moviepy.editor import VideoFileClip
import os
import torch
import matplotlib.pyplot as plt
import random
from torch.utils.data import Dataset
from transformers import VivitImageProcessor
# load libraries
from huggingface_hub import hf_hub_download
from ultralytics import YOLO
from supervision import Detections
from PIL import Image
from face import detect_face
import torchvision
import numpy as np

def sample_frame(video_path: os.PathLike, time: float = 0.0):
    # open a mov video file, sample a frame, and return it as a numpy array
    with VideoFileClip(video_path, audio=False) as clip:
        # Sample a frame: get the first frame
        print(f'clip.fps: {clip.fps}')
        frame = clip.get_frame(time)  # get the frame at t=0 seconds
        # h, w, c
    
    # get the top square of the frame via crop, and resize it to 224x224 using bilinear interpolation
    frame = frame[int(frame.shape[1]*0.2):int(1.2*frame.shape[1]), :, :]
    frame = torch.tensor(frame).permute(2, 0, 1).float() / 255.
    frame = torch.nn.functional.interpolate(frame.unsqueeze(0), size=224, mode='bilinear', align_corners=False).squeeze(0)
    return frame

def sample_32_frames(video_path: os.PathLike, interval: float):
    frames = []
    with VideoFileClip(video_path, audio=False) as clip:
        start = random.uniform(0, clip.duration - interval)
        
        for _1, t in enumerate(torch.arange(start, start + interval, interval/32)):
            if _1 == 0:
                _, (x1, y1, x2, y2) = detect_face(clip.get_frame(t))
            frame = frame[y1:y2, x1:x2]
            frames.append(frame.transpose(2, 0, 1))
            # h, w, c
    return frames[:32]

class MyDataset(Dataset):
    def __init__(self, root, samples_per_clip=1, sample_length=4):
        self.root = root
        self.samples_per_clip = samples_per_clip
        self.sample_length = sample_length
        self.pp1 = VivitImageProcessor.from_pretrained("google/vivit-b-16x2")

    def __len__(self):
        return 120 * self.samples_per_clip

    def __getitem__(self, idx):
        n = idx % 120
        k = n // 3
        f = n % 3
        x = None
        for ext in ['.mov', '.MOV', '.mp4', '.MP4', '.m4v']:
            video_path = os.path.join(self.root, f'{k+1:02d}', f'{5*f}{ext}')
            if os.path.exists(video_path):
                x = sample_32_frames(video_path, self.sample_length)
                break
        if x is None:
            print(video_path)
            raise RuntimeError('Something went wrong')
        x = self.pp1(x, return_tensors='pt')
        x['labels'] = torch.tensor(f, dtype=torch.long)# / 2
        return x

class MyValDataset(Dataset):
    def __init__(self, root, samples_per_clip=1, sample_length=4):
        self.root = root
        self.samples_per_clip = samples_per_clip
        self.sample_length = sample_length
        self.pp1 = VivitImageProcessor.from_pretrained("google/vivit-b-16x2")

    def __len__(self):
        return 24 * self.samples_per_clip

    def __getitem__(self, idx):
        n = idx % 24
        k = n // 3
        f = n % 3
        x = None
        for ext in ['.mov', '.MOV', '.mp4', '.MP4', '.m4v']:
            video_path = os.path.join(self.root, f'{k+41:02d}', f'{5*f}{ext}')
            if os.path.exists(video_path):
                x = sample_32_frames(video_path, self.sample_length)
                break
        if x is None:
            print(video_path)
            raise RuntimeError('Something went wrong')
        x = self.pp1(x, return_tensors='pt')
        x['labels'] = torch.tensor(f, dtype=torch.long)# / 2
        # x['labels'] = torch.tensor(f) / 2
        return x


class DDD(Dataset):
    def __init__(self, root='/scratch/hina/drowsy_ds', transforms=[
        torchvision.transforms.Resize((224, 224)),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.RandomHorizontalFlip(),
        torchvision.transforms.RandomRotation(5),
        torchvision.transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ], split=(0, 1)) -> None:
        super().__init__()
        self.root = root
        self.drowsy_dir = os.path.join(root, 'Drowsy')
        self.alert_dir = os.path.join(root, 'Non Drowsy')
        self.drowsy_paths = [os.path.join(self.drowsy_dir, p) for p in os.listdir(self.drowsy_dir)]
        self.drowsy_paths = self.drowsy_paths[int(split[0]*len(self.drowsy_paths)):int(split[1]*len(self.drowsy_paths))]
        alert_paths = [os.path.join(self.alert_dir, p) for p in os.listdir(self.alert_dir)]
        alert_paths = alert_paths[int(split[0]*len(alert_paths)):int(split[1]*len(alert_paths))]
        self.paths = self.drowsy_paths + alert_paths
        self.drowsy_paths = set(self.drowsy_paths)
        random.shuffle(self.paths)
        self.transforms = torchvision.transforms.Compose(transforms)

    def __len__(self):
        return len(self.paths)
    def __getitem__(self, idx):
        path = self.paths[idx]
        is_drowsy = path in self.drowsy_paths
        img = self.transforms(Image.open(path))
        return {'image': img, 'label': torch.tensor(is_drowsy, dtype=torch.long)}

import pandas as pd
class D2(Dataset):
    def __init__(self, root='/scratch/hina/drowsy2', split='train', transforms=[
        torchvision.transforms.Resize((224, 224)),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.RandomHorizontalFlip(),
        torchvision.transforms.RandomRotation(5),
        torchvision.transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ]) -> None:
        super().__init__()
        self.root = os.path.join(root, split)
        # load _annotations.csv
        self.data = []
        with open(os.path.join(self.root, f'_annotations.csv')) as f:
            self.csv = pd.read_csv(f)
        #filename,width,height,class,xmin,ymin,xmax,ymax
        self.transforms = torchvision.transforms.Compose(transforms)
    def __len__(self):
        return len(self.csv)
    def __getitem__(self, idx):
        row = self.csv.iloc[idx]
        img = np.array(Image.open(os.path.join(self.root, row['filename'])))
        img, _ = detect_face(img)
        img = Image.fromarray(img)
        img = self.transforms(img)

        return {'image': img, 'label': torch.tensor(row['class'] == 'drowsy', dtype=torch.long)}