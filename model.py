"""
PyTorch LSTM Model Definition for Sign Language Recognition
"""
import torch
import torch.nn as nn


class CustomLSTM(nn.Module):
    """
    LSTM-based model for gesture recognition from MediaPipe landmarks.

    Architecture:
    - 2-layer LSTM with dropout
    - Fully connected layers
    - Softmax output for multi-class classification
    """
    def __init__(self, input_size=258, hidden_size=64, num_classes=11):
        super(CustomLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers=2,
            batch_first=True,
            dropout=0.3
        )
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(hidden_size, 64)
        self.output_layer = nn.Linear(64, num_classes)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]  # Get last time step
        out = self.dropout(out)
        out = torch.relu(self.fc1(out))
        out = self.output_layer(out)
        return out
