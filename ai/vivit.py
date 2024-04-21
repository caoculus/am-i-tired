# Load model directly
from transformers import VivitForVideoClassification
from dl import MyDataset, MyValDataset
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch import nn
import torch
# import grad scaler
from torch.cuda.amp import GradScaler, autocast
from tqdm import tqdm
# Load model directly
model = VivitForVideoClassification.from_pretrained("google/vivit-b-16x2")

model.num_labels = 3
model.classifier = nn.Linear(768, 3)
model.cuda()

def accuracy(preds, labels):
    return (preds.argmax(dim=1) == labels).float().mean().item()

# def accuracy(preds, labels):
#     return (((0 <= preds) & (preds <= 0.33) & (0 <= labels) & (labels<= 0.33)).sum().item() + \
#               ((0.33 < preds) & (preds <= 0.66) & (0.33 < labels) & (labels <= 0.66)).sum().item() + \
#               ((0.66 < preds) & (preds <= 1) & (0.66 < labels) & (labels <= 1)).sum().item()) / len(labels)


print(sum(p.numel() for p in model.parameters() if p.requires_grad))

# Load dataset
ds = MyDataset('/scratch/hina/alert_ds', samples_per_clip=20, sample_length=3.2)
dl = DataLoader(ds, batch_size=6, shuffle=True, num_workers=12)
ds_= MyValDataset('/scratch/hina/alert_ds', samples_per_clip=5, sample_length=3.2)
dl_= DataLoader(ds_, batch_size=6, shuffle=False, num_workers=12)
optimizer = AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)
scaler = GradScaler()

def t_f_1_epoch(model, dl, optim, scaler):
    model.train()
    pbar = tqdm(enumerate(dl), total=len(dl))
    total_loss = 0
    total_acc = 0

    accum = 4

    for i, batch in pbar:
        inputs = batch['pixel_values'].squeeze(1).cuda()
        labels = batch['labels'].cuda()
        with autocast():
            outputs = model(inputs)
            loss = nn.functional.cross_entropy(outputs.logits, labels)
            # loss = nn.functional.binary_cross_entropy_with_logits(outputs.logits.view(-1), labels.view(-1))
            # preds = nn.functional.sigmoid(outputs.logits)
            acc = accuracy(outputs.logits, labels)
        scaler.scale(loss).backward()

        if i % accum == accum - 1:
            scaler.step(optim)
            scaler.update()
            optim.zero_grad()

        total_loss += loss.item()
        total_acc += acc

        pbar.set_description(f'loss: {total_loss/(i+1):.4f}({loss.item():.2f}), acc: {100*total_acc/(i+1):.2f}({100*acc:.0f})')

    # save model
    torch.save(model.state_dict(), 'model.pth')



class MyModel():
    def __init__(self):
        from torchvision.models import resnet18
        self.model = resnet18(pretrained=False)
        self.model.fc = nn.Linear(512, 1)
        self.model.load_state_dict(torch.load('r18.pth'))
        self.model.cuda()
    
    def __call__(self, x):
        output = self.model(x[:,0,:,:,:])
        zeros = torch.zeros_like(output)
        minus_output = -output
        return torch.cat([output, zeros, minus_output], dim=1)
    
    def eval(self):
        self.model.eval()
@torch.no_grad()
def val(model, dl):
    model.eval()
    pbar = tqdm(enumerate(dl), total=len(dl))
    total_acc = 0

    for i, batch in pbar:
        inputs = batch['pixel_values'].squeeze(1).cuda()
        labels = batch['labels'].cuda()
        with autocast():
            outputs = model(inputs)
            acc = accuracy(outputs.logits, labels)

        total_acc += acc
        pbar.set_description(f'acc: {100*total_acc/(i+1):.2f}({100*acc:.0f})')

for i in range(5):
    t_f_1_epoch(model, dl, optimizer, scaler)
    val(model, dl_)
# model2 = MyModel()
# val(model2, dl)

# B,32,3,224,224
# preprocessor([torch.randint(low=0,high=256,size=(3,224,225)) for _ in range(32)])
