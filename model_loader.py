import llama_cpp
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as a .py file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "models", "Dolphin3.0-Llama3.2-3B-Q5_K_M.gguf")

if not os.path.exists(model_path):
    raise ValueError(f"Model file not found at: {model_path}. Please ensure it's in the 'models' directory.")

try:
    llm_model = llama_cpp.Llama(model_path=model_path, chat_format="llama-2", n_ctx=8192, n_gpu_layers=-1)
    print(f"Llama model loaded successfully from {model_path}")
except Exception as e:
    print(f"Error loading Llama model from {model_path}: {e}")
    print("Please ensure the model file is valid and compatible with your llama-cpp-python installation.")
    print("Consider re-downloading the model or updating llama-cpp-python.")
    sys.exit(1) # Exit if the core model cannot be loaded
