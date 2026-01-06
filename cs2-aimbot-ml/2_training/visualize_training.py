"""
Training Visualization Script
==============================
Zeigt Training-Metriken und Plots in einem übersichtlichen Dashboard.

Verwendung:
    python visualize_training.py

Zeigt:
- Loss Kurven
- mAP Entwicklung
- Precision/Recall
- Training Samples
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from colorama import Fore, init

init(autoreset=True)
sns.set_style("darkgrid")

def visualize_training(run_dir="../models/cs2_target_detector_n"):
    """
    Visualisiert Training-Ergebnisse

    Args:
        run_dir: Pfad zum Training-Run Ordner
    """

    results_csv = os.path.join(run_dir, "results.csv")

    if not os.path.exists(results_csv):
        print(f"{Fore.RED}Keine Trainings-Daten gefunden in {run_dir}")
        print(f"{Fore.YELLOW}Tipp: Führe zuerst train_model.py aus!")
        return

    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}CS2 Training Visualisierung")
    print(f"{Fore.GREEN}{'='*70}\n")

    # Lade Results
    df = pd.read_csv(results_csv)
    df.columns = df.columns.str.strip()  # Entferne Whitespace

    print(f"{Fore.WHITE}Gefundene Epochs: {Fore.CYAN}{len(df)}")

    # Erstelle Figure mit Subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('CS2 Target Detection - Training Progress', fontsize=16, fontweight='bold')

    # Plot 1: Loss Curves
    ax1 = axes[0, 0]
    if 'train/box_loss' in df.columns:
        ax1.plot(df.index, df['train/box_loss'], label='Box Loss', linewidth=2)
    if 'train/cls_loss' in df.columns:
        ax1.plot(df.index, df['train/cls_loss'], label='Class Loss', linewidth=2)
    if 'train/dfl_loss' in df.columns:
        ax1.plot(df.index, df['train/dfl_loss'], label='DFL Loss', linewidth=2)

    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Losses (sollten sinken)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: mAP (Mean Average Precision)
    ax2 = axes[0, 1]
    if 'metrics/mAP50(B)' in df.columns:
        ax2.plot(df.index, df['metrics/mAP50(B)'], label='mAP@50', linewidth=2, color='green')
    if 'metrics/mAP50-95(B)' in df.columns:
        ax2.plot(df.index, df['metrics/mAP50-95(B)'], label='mAP@50-95', linewidth=2, color='blue')

    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('mAP')
    ax2.set_title('Mean Average Precision (sollte steigen)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 1])

    # Plot 3: Precision & Recall
    ax3 = axes[1, 0]
    if 'metrics/precision(B)' in df.columns:
        ax3.plot(df.index, df['metrics/precision(B)'], label='Precision', linewidth=2, color='orange')
    if 'metrics/recall(B)' in df.columns:
        ax3.plot(df.index, df['metrics/recall(B)'], label='Recall', linewidth=2, color='purple')

    ax3.set_xlabel('Epoch')
    ax3.set_ylabel('Score')
    ax3.set_title('Precision & Recall')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim([0, 1])

    # Plot 4: Learning Rate
    ax4 = axes[1, 1]
    lr_cols = [col for col in df.columns if 'lr' in col.lower()]
    for col in lr_cols:
        ax4.plot(df.index, df[col], label=col, linewidth=2)

    ax4.set_xlabel('Epoch')
    ax4.set_ylabel('Learning Rate')
    ax4.set_title('Learning Rate Schedule')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    # Speichere Plot
    output_path = os.path.join(run_dir, "training_visualization.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"{Fore.GREEN}✓ Visualisierung gespeichert: {Fore.CYAN}{output_path}")

    plt.show()

    # Statistiken ausgeben
    print(f"\n{Fore.YELLOW}Training Statistiken:")
    print(f"{Fore.GREEN}{'─'*70}")

    if 'metrics/mAP50(B)' in df.columns:
        best_map50 = df['metrics/mAP50(B)'].max()
        best_epoch = df['metrics/mAP50(B)'].idxmax()
        print(f"{Fore.WHITE}Beste mAP@50: {Fore.CYAN}{best_map50:.3f} {Fore.WHITE}(Epoch {best_epoch})")

    if 'metrics/precision(B)' in df.columns:
        final_precision = df['metrics/precision(B)'].iloc[-1]
        print(f"{Fore.WHITE}Finale Precision: {Fore.CYAN}{final_precision:.3f}")

    if 'metrics/recall(B)' in df.columns:
        final_recall = df['metrics/recall(B)'].iloc[-1]
        print(f"{Fore.WHITE}Finale Recall: {Fore.CYAN}{final_recall:.3f}")

    print(f"{Fore.GREEN}{'─'*70}\n")

    # Interpretations-Hilfe
    print(f"{Fore.YELLOW}Interpretation:")
    print(f"{Fore.WHITE}mAP@50:")
    if 'metrics/mAP50(B)' in df.columns:
        map50 = df['metrics/mAP50(B)'].iloc[-1]
        if map50 > 0.9:
            print(f"  {Fore.GREEN}✓ Exzellent! (>{0.9:.1%})")
        elif map50 > 0.7:
            print(f"  {Fore.CYAN}✓ Gut! (>{0.7:.1%})")
        elif map50 > 0.5:
            print(f"  {Fore.YELLOW}⚠ OK, könnte besser sein (>{0.5:.1%})")
        else:
            print(f"  {Fore.RED}✗ Noch viel Raum für Verbesserung")

        print(f"{Fore.WHITE}Tipps zur Verbesserung:")
        if map50 < 0.7:
            print(f"  • Sammle mehr Training-Daten (Ziel: 500+ gelabelte Bilder)")
            print(f"  • Trainiere länger (mehr Epochs)")
            print(f"  • Verwende größeres Model (yolov8s statt yolov8n)")

    print(f"{Fore.GREEN}{'='*70}\n")

if __name__ == "__main__":
    try:
        # Versuche automatisch den neuesten Run zu finden
        models_dir = "../models"
        if os.path.exists(models_dir):
            runs = [d for d in os.listdir(models_dir) if d.startswith("cs2_target_detector")]
            if runs:
                latest_run = sorted(runs)[-1]
                run_dir = os.path.join(models_dir, latest_run)
                visualize_training(run_dir)
            else:
                print(f"{Fore.RED}Keine Training-Runs gefunden")
        else:
            print(f"{Fore.RED}Models-Ordner nicht gefunden")

    except Exception as e:
        print(f"{Fore.RED}Fehler: {e}")
