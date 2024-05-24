import torch
import torch.nn as nn
import torch.optim as optim
from model import SparringCNN
from torch.utils.data import random_split, DataLoader
from torchvision.transforms import v2
from torchvision.datasets import ImageFolder
from progress_bar import ProgressBar

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

data_path = "data/"

transforms = v2.Compose([
    v2.RandomHorizontalFlip(p=0.5),
    v2.PILToTensor(),
    v2.ToDtype(torch.float32, scale=True),
    v2.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])


data = ImageFolder(root=data_path, transform=transforms)

train_size = 0.8
val_size = 1 - train_size
train_set, val_set = random_split(data, [train_size, val_size])

batch_size = 32
train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False)

model = SparringCNN()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 1
model = model.to(device)

print("Started Training")
for epoch in range(num_epochs):
    model.train()
    train_loss = 0.0
    bar = ProgressBar(len(train_loader))
    bar.update_message("Training")
    bar.print()
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item() * images.size(0)
        bar.increment()
        bar.print()
    bar.print()
    print()

    bar = ProgressBar(len(val_loader))
    bar.update_message("Validation")
    bar.print()
    model.eval()
    val_loss = 0.0
    val_corrects = 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            val_corrects += torch.sum(preds == labels.data)
            bar.increment()
            bar.print()
    bar.print()
    print()

    train_loss = train_loss / len(train_loader.dataset)
    val_loss = val_loss / len(val_loader.dataset)
    val_accuracy = val_corrects.double() / len(val_loader.dataset)
    print(f"Epoch {epoch + 1}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, Val Accuracy: {val_accuracy:.4f}")

torch.save(model.state_dict(), "./model.pth")
