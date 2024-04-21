import torch
import open_clip

model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms('hf-hub:laion/CLIP-ViT-L-14-DataComp.XL-s13B-b90K', cache_dir='/scratch/hina/clip-cache')
tokenizer = open_clip.get_tokenizer('hf-hub:laion/CLIP-ViT-L-14-DataComp.XL-s13B-b90K')

prompts = [
    'drowsy and sleepy',
    'awake and alert',
    'a human face'
]

from dl import MyDataset

dataset = MyDataset('/scratch/hina/alert_ds', 1, 3.2)
print(dataset[0]['labels'])
# get the text features
text_features = tokenizer(prompts)


with torch.no_grad():
    image_features = model.encode_image(dataset[0]['pixel_values'].squeeze(0))
    text_features = model.encode_text(text_features)

    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)

    # get the similarity score
    similarity = model.logit_scale * (image_features @ text_features.T)

print(similarity)

