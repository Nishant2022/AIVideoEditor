import torch
import torch.nn as nn


class SparringCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.relu = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.pool5 = nn.MaxPool2d(kernel_size=5, stride=5)
        self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=1, padding=2)
        self.conv2 = nn.Conv2d(16, 64, kernel_size=5, stride=1, padding=2)
        self.conv3 = nn.Conv2d(64, 32, kernel_size=5, stride=1, padding=2)
        self.fc1 = nn.Linear(32 * 16 * 9, 64)
        self.fc2 = nn.Linear(64, 2)

    def forward(self, x):
        N, C, H, W = x.shape
        x = self.pool5(self.relu(self.conv1(x)))
        x = self.pool2(self.relu(self.conv2(x)))
        x = self.pool2(self.relu(self.conv3(x)))
        x = torch.reshape(x, (N, 32 * 16 * 9))
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x
