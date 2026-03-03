"""
Train YOLOv8 for pothole detection.
Completely free using Ultralytics open-source library.
"""
import os
import sys
import argparse
import shutil
from pathlib import Path


def train_pothole_model(
    data_yaml: str,
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    model_size: str = "n",  # n, s, m, l, x (nano to extra-large)
    device: str = "",  # '' = auto, 'cpu', '0' for GPU
    project_name: str = "pothole_detection",
):
    from ultralytics import YOLO

    # Start from a pretrained YOLOv8 model (free download)
    base_model = f"yolov8{model_size}.pt"
    print(f"\n{'='*60}")
    print(f"TRAINING YOLOV8 POTHOLE DETECTOR")
    print(f"{'='*60}")
    print(f"  Base model: {base_model}")
    print(f"  Dataset: {data_yaml}")
    print(f"  Epochs: {epochs}")
    print(f"  Image size: {imgsz}")
    print(f"  Batch size: {batch}")
    print(f"{'='*60}\n")

    model = YOLO(base_model)

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project=project_name,
        name="train",
        patience=20,
        save=True,
        save_period=10,
        plots=True,
        verbose=True,
        # Augmentation settings for road images
        hsv_h=0.015,
        hsv_s=0.5,
        hsv_v=0.3,
        degrees=5.0,
        translate=0.1,
        scale=0.3,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
    )

    # Copy best model to trained_models directory
    best_model = Path(project_name) / "train" / "weights" / "best.pt"
    target = Path(__file__).parent.parent / "trained_models" / "best.pt"
    target.parent.mkdir(parents=True, exist_ok=True)

    if best_model.exists():
        shutil.copy2(best_model, target)
        print(f"\n✅ Best model saved to: {target}")
    else:
        print(f"\n⚠️ Best model not found at {best_model}")

    # Validation
    metrics = model.val()
    print(f"\n📊 Validation Results:")
    print(f"   mAP50: {metrics.box.map50:.4f}")
    print(f"   mAP50-95: {metrics.box.map:.4f}")
    print(f"   Precision: {metrics.box.mp:.4f}")
    print(f"   Recall: {metrics.box.mr:.4f}")

    return str(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8 Pothole Detector")
    parser.add_argument("--data", type=str, required=True, help="Path to data.yaml")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--model-size", type=str, default="n", choices=["n", "s", "m", "l", "x"])
    parser.add_argument("--device", type=str, default="")
    args = parser.parse_args()

    train_pothole_model(
        data_yaml=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        model_size=args.model_size,
        device=args.device,
    )