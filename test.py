import os

threshold_mb = 10
root_dir = '.'  # change if your root folder is different

for dirpath, _, filenames in os.walk(root_dir):
    for f in filenames:
        filepath = os.path.join(dirpath, f)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if size_mb > threshold_mb:
            print(f"{filepath} - {size_mb:.2f} MB")
