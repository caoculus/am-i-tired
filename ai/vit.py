from flash_attn.models.vit import VisionTransformer

# import a pretrained resnet18 model from torch hub 
import torch
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader
from torchvision.models import vit_b_16
from dl import DDD, D2

# Load the pretrained model
model = vit_b_16(pretrained=True)
model.heads[-1] = nn.Linear(768, 1)
model.num_classes = 1
model.cuda()

# Load the dataset
ds = D2(split='train')
ds_val = D2(split='valid')
ds2 = DDD(split=(0, 0.1))
dl = DataLoader(ds, batch_size=96, shuffle=True, num_workers=24)
dl2 = DataLoader(ds2, batch_size=96, shuffle=True, num_workers=24)
dl_val = DataLoader(ds_val, batch_size=48, shuffle=False, num_workers=12)
optimizer = AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)
criterion = nn.BCEWithLogitsLoss()

def train_epoch(model, dl, optimizer):
    model.train()
    for i, batch in enumerate(dl):
        inputs = batch['image'].cuda()
        labels = batch['label'].cuda()

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels.float().view(-1, 1))
        loss.backward()
        optimizer.step()
        acc = ((outputs.flatten() > 0) == labels).float().mean()

        print(f'loss: {loss.item():.4f}, acc: {100*acc:.2f}')
    # save model
    torch.save(model.state_dict(), 'model.pth')

@torch.no_grad()
def val_epoch(model, dl):
    model.eval()
    total_acc = 0
    for i, batch in enumerate(dl):
        inputs = batch['image'].cuda()
        labels = batch['label'].cuda()

        outputs = model(inputs)
        acc = ((outputs.flatten() > 0) == labels).float().mean()
        total_acc += acc
    print(f'val acc: {100*total_acc/(i+1):.2f}')

for i in range(10):
    train_epoch(model, dl, optimizer)
    val_epoch(model, dl_val)


