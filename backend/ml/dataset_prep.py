"""
Download and prepare a free pothole detection dataset.
Uses Roboflow Universe (free tier - create account at roboflow.com).
Alternative: Kaggle pothole datasets.
"""
import os
import subprocess
import sys


def download_roboflow_dataset():
    """
    Option 1: Roboflow (recommended - best quality)
    1. Go to https://universe.roboflow.com
    2. Search "pothole detection"  
    3. Pick a dataset (e.g., "Pothole Detection Computer Vision Project")
    4. Click "Download" → "YOLOv8" format → get the code snippet
    """
    try:
        from roboflow import Roboflow

        # Replace with YOUR free Roboflow API key
        rf = Roboflow(api_key="YOUR_FREE_ROBOFLOW_API_KEY")

        # Example: Pothole Detection dataset
        project = rf.workspace("your-workspace").project("pothole-detection")
        dataset = project.version(1).download("yolov8")

        print(f"Dataset downloaded to: {dataset.location}")
        return dataset.location

    except Exception as e:
        print(f"Roboflow download failed: {e}")
        print("Falling back to manual dataset creation...")
        return create_sample_dataset()


def download_kaggle_dataset():
    """
    Option 2: Kaggle pothole dataset (free)
    1. pip install kaggle
    2. Set up Kaggle API credentials (~/.kaggle/kaggle.json)
    3. Download a pothole dataset
    """
    os.makedirs("datasets/pothole", exist_ok=True)
    subprocess.run([
        "kaggle", "datasets", "download",
        "-d", "sachinpatel21/pothole-image-dataset",
        "-p", "datasets/pothole", "--unzip"
    ])
    print("Kaggle dataset downloaded!")


def create_sample_dataset():
    """
    Option 3: Create a minimal sample dataset for testing.
    In production, use a real annotated dataset.
    """
    import numpy as np
    from PIL import Image, ImageDraw
    import yaml
    import random

    base_dir = os.path.join(os.path.dirname(__file__), "..", "datasets", "pothole")
    for split in ["train", "val"]:
        os.makedirs(os.path.join(base_dir, split, "images"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, split, "labels"), exist_ok=True)

    for split, count in [("train", 200), ("val", 50)]:
        for idx in range(count):
            img = Image.new("RGB", (640, 640), (70 + random.randint(-20, 20),) * 3)
            draw = ImageDraw.Draw(img)

            # Road surface
            draw.rectangle([80, 0, 560, 640], fill=(55, 55, 55))
            for y in range(0, 640, 40):
                draw.rectangle([315, y, 325, y + 20], fill=(180, 180, 180))

            labels = []
            num_potholes = random.choices([0, 1, 2, 3], weights=[25, 35, 25, 15])[0]

            for _ in range(num_potholes):
                cx = random.uniform(0.2, 0.8)
                cy = random.uniform(0.1, 0.9)
                w = random.uniform(0.04, 0.18)
                h = random.uniform(0.03, 0.14)

                px = int(cx * 640 - w * 640 / 2)
                py = int(cy * 640 - h * 640 / 2)
                pw = int(w * 640)
                ph = int(h * 640)

                draw.ellipse([px, py, px + pw, py + ph], fill=(25, 20, 15), outline=(15, 10, 5))
                inner_w, inner_h = pw // 2, ph // 2
                draw.ellipse(
                    [px + pw // 4, py + ph // 4, px + pw // 4 + inner_w, py + ph // 4 + inner_h],
                    fill=(10, 5, 3),
                )

                labels.append(f"0 {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

            # Add noise
            pixels = np.array(img)
            noise = np.random.normal(0, 12, pixels.shape).astype(np.int16)
            pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(pixels)

            img.save(os.path.join(base_dir, split, "images", f"img_{idx:04d}.jpg"))
            with open(os.path.join(base_dir, split, "labels", f"img_{idx:04d}.txt"), "w") as f:
                f.write("\n".join(labels))

    # Create data.yaml
    data_yaml = {
        "path": os.path.abspath(base_dir),
        "train": "train/images",
        "val": "val/images",
        "nc": 1,
        "names": ["pothole"],
    }
    yaml_path = os.path.join(base_dir, "data.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(data_yaml, f)

    print(f"Sample dataset created at: {base_dir}")
    print(f"  Train images: {200}, Val images: {50}")
    return base_dir


if __name__ == "__main__":
    print("=" * 60)
    print("POTHOLE DATASET PREPARATION")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Roboflow (recommended, free tier)")
    print("  2. Kaggle pothole dataset")
    print("  3. Generate synthetic sample dataset")

    choice = input("\nSelect option (1/2/3): ").strip()

    if choice == "1":
        download_roboflow_dataset()
    elif choice == "2":
        download_kaggle_dataset()
    else:
        create_sample_dataset()