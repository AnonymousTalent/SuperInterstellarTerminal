import torch
import pytorch_lightning as pl

class PhishingDetector(pl.LightningModule):
    """A PyTorch Lightning module to detect phishing URLs."""
    def __init__(self, input_features=10, hidden_dim=5):
        super().__init__()
        self.model = torch.nn.Sequential(
            torch.nn.Linear(input_features, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, 2)
        )
        self.save_hyperparameters()

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = torch.nn.functional.cross_entropy(y_hat, y)
        self.log('train_loss', loss)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.001)

    def predict_url(self, url_features):
        self.eval()
        with torch.no_grad():
            logits = self(url_features)
            _, predicted_class = torch.max(logits, 1)
            return "Phishing" if predicted_class.item() == 1 else "Legitimate"

def get_mock_features():
    """Generates a mock feature tensor for a single URL for demonstration."""
    return torch.randn(1, 10)