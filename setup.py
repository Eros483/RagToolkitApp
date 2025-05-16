import os
import urllib.request

MODEL_URL = "https://huggingface.co/Triangle104/Dolphin3.0-Llama3.2-3B-Q5_K_M-GGUF/resolve/main/dolphin3.0-llama3.2-3b-q5_k_m.gguf"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "dolphin3.0-llama3.2-3b-q5_k_m.gguf")

def download_model():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        print(f"Created directory: {MODEL_DIR}")
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading model from {MODEL_URL} ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print(f"Model downloaded and saved to {MODEL_PATH}")
    else:
        print(f"Model already exists at {MODEL_PATH}")

if __name__ == "__main__":
    download_model()
