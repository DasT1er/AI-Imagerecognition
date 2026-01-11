"""
Imitation Learning Trainer
===========================
Trainiert Bot VON DEINEN Aufnahmen!

Behavioral Cloning:
- Lernt deine Actions direkt von Screenshots + Inputs
- CNN für Bilder + FC für Game State
- Supervised Learning (keine Rewards nötig!)

Nach dem Training kann der Bot spielen wie DU!
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import os
from PIL import Image
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt


class HumanGameplayDataset(Dataset):
    """
    Dataset from human gameplay recordings

    Loads from: data/human_gameplay/session_*/
    """

    def __init__(self, data_dir="../../data/human_gameplay", screen_size=(84, 84)):
        """
        Initialize dataset

        Args:
            data_dir: Directory containing session folders
            screen_size: Size to resize images
        """
        self.data_dir = data_dir
        self.screen_size = screen_size

        # Load all sessions
        self.samples = []
        self._load_sessions()

        print(f"📊 Dataset loaded: {len(self.samples)} samples from {self.num_sessions} sessions")

    def _load_sessions(self):
        """Load all session data"""
        self.num_sessions = 0

        if not os.path.exists(self.data_dir):
            print(f"⚠️  No data directory found: {self.data_dir}")
            return

        for session_folder in os.listdir(self.data_dir):
            if not session_folder.startswith('session_'):
                continue

            session_path = os.path.join(self.data_dir, session_folder)
            data_file = os.path.join(session_path, 'session_data.json')

            if not os.path.exists(data_file):
                continue

            # Load session
            with open(data_file, 'r') as f:
                session_data = json.load(f)

            # Add samples
            for frame_data in session_data['data']:
                # Image path
                img_path = os.path.join(session_path, 'images', frame_data['image'])

                if not os.path.exists(img_path):
                    continue

                # Convert inputs to action
                action = self._inputs_to_action(frame_data['keys'], frame_data['mouse'])

                self.samples.append({
                    'image_path': img_path,
                    'action': action,
                    'keys': frame_data['keys'],
                    'mouse': frame_data['mouse']
                })

            self.num_sessions += 1

    def _inputs_to_action(self, keys, mouse):
        """
        Convert human inputs to discrete action

        Action Space (20 actions):
            0-7:   Movement combinations
            8:     Jump
            9:     Crouch
            10:    Walk
            11:    Shoot
            12:    Reload
            13-15: Switch weapon (1, 2, 3)
            16-19: Economy actions (simplified)
        """
        # Movement (0-7)
        forward = keys['w']
        back = keys['s']
        left = keys['a']
        right = keys['d']

        if forward and left:
            action = 5  # Forward-left
        elif forward and right:
            action = 6  # Forward-right
        elif back and left:
            action = 7  # Back-left
        elif forward:
            action = 1  # Forward
        elif back:
            action = 2  # Back
        elif left:
            action = 3  # Left
        elif right:
            action = 4  # Right
        else:
            action = 0  # Idle

        # Special actions (override movement)
        if keys['space']:
            action = 8  # Jump
        elif keys['ctrl']:
            action = 9  # Crouch
        elif keys['shift']:
            action = 10  # Walk
        elif mouse['left_click']:
            action = 11  # Shoot
        elif keys['r']:
            action = 12  # Reload
        elif keys['1']:
            action = 13  # Weapon 1
        elif keys['2']:
            action = 14  # Weapon 2
        elif keys['3']:
            action = 15  # Weapon 3
        elif keys['e']:
            action = 19  # Use (plant/defuse)

        return action

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        """Get sample"""
        sample = self.samples[idx]

        # Load image
        img = Image.open(sample['image_path']).convert('RGB')
        img = img.resize(self.screen_size, Image.Resampling.LANCZOS)

        # Convert to tensor
        img_tensor = torch.from_numpy(np.array(img)).float() / 255.0
        img_tensor = img_tensor.permute(2, 0, 1)  # HWC -> CHW

        # Action
        action = torch.tensor(sample['action'], dtype=torch.long)

        return img_tensor, action


class ImitationNetwork(nn.Module):
    """
    Neural network for imitation learning

    Architecture:
        - CNN: Extract visual features
        - FC: Predict action probabilities
    """

    def __init__(self, num_actions=20, screen_size=(84, 84)):
        """
        Initialize network

        Args:
            num_actions: Number of discrete actions
            screen_size: Input image size
        """
        super().__init__()

        self.num_actions = num_actions

        # CNN for visual features
        self.cnn = nn.Sequential(
            # 84x84x3 -> 20x20x32
            nn.Conv2d(3, 32, kernel_size=8, stride=4, padding=2),
            nn.ReLU(),

            # 20x20x32 -> 9x9x64
            nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),

            # 9x9x64 -> 7x7x64
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),

            nn.Flatten()
        )

        # Calculate CNN output size DYNAMICALLY
        with torch.no_grad():
            dummy_input = torch.zeros(1, 3, screen_size[0], screen_size[1])
            cnn_output_size = self.cnn(dummy_input).shape[1]

        # Fully connected layers
        self.fc = nn.Sequential(
            nn.Linear(cnn_output_size, 512),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(256, num_actions)
        )

    def forward(self, x):
        """
        Forward pass

        Args:
            x: Image tensor [B, 3, H, W]

        Returns:
            Action logits [B, num_actions]
        """
        features = self.cnn(x)
        logits = self.fc(features)
        return logits


class ImitationTrainer:
    """Trainer for imitation learning"""

    def __init__(
        self,
        data_dir="../../data/human_gameplay",
        output_dir="../../models",
        screen_size=(84, 84),
        batch_size=32,
        learning_rate=1e-4,
        device=None
    ):
        """
        Initialize trainer

        Args:
            data_dir: Directory with gameplay recordings
            output_dir: Where to save trained model
            screen_size: Image size
            batch_size: Training batch size
            learning_rate: Learning rate
            device: 'cuda' or 'cpu'
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.screen_size = screen_size
        self.batch_size = batch_size
        self.learning_rate = learning_rate

        # Device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        print(f"🎮 Imitation Learning Trainer")
        print(f"   Device: {self.device}")
        print(f"   Batch Size: {batch_size}")
        print(f"   Learning Rate: {learning_rate}\n")

        # Dataset
        self.dataset = HumanGameplayDataset(data_dir, screen_size)

        if len(self.dataset) == 0:
            raise ValueError(f"No data found in {data_dir}! Please record gameplay first.")

        # Split train/val
        train_size = int(0.9 * len(self.dataset))
        val_size = len(self.dataset) - train_size
        self.train_dataset, self.val_dataset = torch.utils.data.random_split(
            self.dataset, [train_size, val_size]
        )

        print(f"   Train Samples: {len(self.train_dataset)}")
        print(f"   Val Samples: {len(self.val_dataset)}\n")

        # DataLoaders (optimized for RTX 3080 Ti)
        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=8,  # 2x more for faster data loading
            pin_memory=True,
            persistent_workers=True  # Keep workers alive between epochs
        )

        self.val_loader = DataLoader(
            self.val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=8,
            pin_memory=True,
            persistent_workers=True
        )

        # Model
        self.model = ImitationNetwork(num_actions=20, screen_size=screen_size)
        self.model.to(self.device)

        # Optimizer and loss
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()

        # Mixed Precision Training (2x faster on RTX 3080 Ti!)
        self.use_amp = torch.cuda.is_available()
        self.scaler = torch.cuda.amp.GradScaler() if self.use_amp else None

        # Training history
        self.train_losses = []
        self.val_losses = []
        self.val_accuracies = []

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        if self.use_amp:
            print("✅ Mixed Precision Training (AMP) enabled - 2x faster!")

    def train(self, num_epochs=50):
        """
        Train model

        Args:
            num_epochs: Number of training epochs
        """
        print(f"🚀 Starting training for {num_epochs} epochs...\n")

        best_val_loss = float('inf')

        for epoch in range(num_epochs):
            # Train
            train_loss, train_acc = self._train_epoch()

            # Validate
            val_loss, val_acc = self._validate()

            # Save history
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.val_accuracies.append(val_acc)

            # Print progress
            print(f"Epoch {epoch+1}/{num_epochs}")
            print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
            print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")

            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self._save_model('best_model.pt')
                print(f"  ✅ New best model saved!\n")
            else:
                print()

            # Save checkpoint every 10 epochs
            if (epoch + 1) % 10 == 0:
                self._save_model(f'checkpoint_epoch_{epoch+1}.pt')

        print(f"✅ Training complete!")
        print(f"   Best Val Loss: {best_val_loss:.4f}")
        print(f"   Best Val Acc: {max(self.val_accuracies):.2f}%\n")

        # Save final model
        self._save_model('final_model.pt')

        # Plot training curves
        self._plot_training_curves()

    def _train_epoch(self):
        """Train one epoch"""
        self.model.train()
        total_loss = 0
        total_correct = 0
        total_samples = 0

        pbar = tqdm(self.train_loader, desc="Training", leave=False)
        for images, actions in pbar:
            images = images.to(self.device, non_blocking=True)
            actions = actions.to(self.device, non_blocking=True)

            self.optimizer.zero_grad()

            # Mixed Precision Forward pass
            if self.use_amp:
                with torch.cuda.amp.autocast():
                    logits = self.model(images)
                    loss = self.criterion(logits, actions)

                # Scaled Backward pass
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                # Regular forward/backward
                logits = self.model(images)
                loss = self.criterion(logits, actions)
                loss.backward()
                self.optimizer.step()

            # Metrics
            total_loss += loss.item() * images.size(0)
            predictions = logits.argmax(dim=1)
            total_correct += (predictions == actions).sum().item()
            total_samples += images.size(0)

            # Update progress bar
            pbar.set_postfix({
                'loss': loss.item(),
                'acc': 100.0 * total_correct / total_samples
            })

        avg_loss = total_loss / total_samples
        accuracy = 100.0 * total_correct / total_samples

        return avg_loss, accuracy

    def _validate(self):
        """Validate model"""
        self.model.eval()
        total_loss = 0
        total_correct = 0
        total_samples = 0

        with torch.no_grad():
            for images, actions in self.val_loader:
                images = images.to(self.device)
                actions = actions.to(self.device)

                # Forward pass
                logits = self.model(images)
                loss = self.criterion(logits, actions)

                # Metrics
                total_loss += loss.item() * images.size(0)
                predictions = logits.argmax(dim=1)
                total_correct += (predictions == actions).sum().item()
                total_samples += images.size(0)

        avg_loss = total_loss / total_samples
        accuracy = 100.0 * total_correct / total_samples

        return avg_loss, accuracy

    def _save_model(self, filename):
        """Save model checkpoint"""
        filepath = os.path.join(self.output_dir, filename)

        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'val_accuracies': self.val_accuracies,
        }, filepath)

    def _plot_training_curves(self):
        """Plot and save training curves"""
        plt.figure(figsize=(12, 4))

        # Loss
        plt.subplot(1, 2, 1)
        plt.plot(self.train_losses, label='Train Loss')
        plt.plot(self.val_losses, label='Val Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training and Validation Loss')
        plt.legend()
        plt.grid(True)

        # Accuracy
        plt.subplot(1, 2, 2)
        plt.plot(self.val_accuracies, label='Val Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy (%)')
        plt.title('Validation Accuracy')
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'training_curves.png'))
        print(f"📊 Training curves saved: {self.output_dir}/training_curves.png")


if __name__ == "__main__":
    """Train imitation learning model"""
    print("\n" + "="*60)
    print("  IMITATION LEARNING TRAINER")
    print("="*60 + "\n")

    print("Instructions:")
    print("  1. Zuerst mit collect_human_data.py Gameplay aufnehmen")
    print("  2. Dann dieses Script starten")
    print("  3. Model trainiert auf DEINEN Actions!\n")

    # Get absolute paths (3 levels up: 3_learning/imitation/ -> ai/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ai_dir = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
    data_dir = os.path.join(ai_dir, 'data', 'human_gameplay')
    output_dir = os.path.join(ai_dir, 'models')

    print(f"📂 Directories:")
    print(f"   Data: {data_dir}")
    print(f"   Output: {output_dir}\n")

    # Auto-detect optimal batch size based on GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9

        print(f"🎮 GPU detected: {gpu_name}")
        print(f"   VRAM: {vram_gb:.1f} GB\n")

        # Optimal batch size based on VRAM
        if vram_gb >= 10:  # RTX 3080 Ti, 3090, 4080, etc.
            batch_size = 128
            print("✅ Using LARGE batch size (128) for high-end GPU!")
        elif vram_gb >= 8:  # RTX 3070, 4070, etc.
            batch_size = 96
            print("✅ Using MEDIUM batch size (96)")
        elif vram_gb >= 6:  # RTX 3060, etc.
            batch_size = 64
            print("✅ Using MEDIUM batch size (64)")
        else:
            batch_size = 32
            print("⚠️  Using SMALL batch size (32) for lower VRAM")
    else:
        batch_size = 16  # CPU mode
        print("⚠️  No GPU detected - using CPU (slow!)")

    print()

    # Create trainer
    trainer = ImitationTrainer(
        data_dir=data_dir,
        output_dir=output_dir,
        batch_size=batch_size,
        learning_rate=1e-4
    )

    # Train
    trainer.train(num_epochs=50)

    print("✅ Training abgeschlossen!")
    print(f"💾 Model gespeichert in: {trainer.output_dir}/")
    print("\nNächster Schritt: test_bot.py zum Testen!")
