# RAG Toolkit

**RAG Toolkit** is a Retrieval-Augmented Generation (RAG) app that uses a local LLaMA GGUF model. It combines a user-friendly GUI with a backend to fetch context and generate responses, all offline.

---

## Features

- Local LLaMA GGUF model integration
- Simple GUI for easy interaction
- Retrieval-augmented generation pipeline
- Minimal dependencies and setup
- Suitable for offline and privacy-sensitive use cases

---

## Getting Started

### Requirements

- Windows 10/11 (tested)
- Python 3.10 (if running from source)

### Running the Executable
1. Clone the repository
1. Download the `.exe` from the [Releases](#) section, in the same directory as the clone.
2. Run ``python download_model.py`` on your terminal from the same directory at which the .exe was installed
3. Run `rag_gui.exe`.
---
### Dependencies
-llama-cpp-python

-PySide6

-faiss-cpu 

-numpy

-pymupdf 

-sentence-transformers

-scikit-learn 

---
### Notes
- Keep the `.exe ` and the  `models` folder together for the app to find the model correctly
- Created with CUDA support on LLAMA-CPP. Recreate executable by cloning repository, disabling cuda, and recompiling .exe with `pyinstaller --onefile --add-binary "C:\Users\caio\miniconda3\envs\rag_new_env\Lib\site-packages\llama_cpp\lib;llama_cpp\lib" frontend.py`, changing the binary's path according to your own llama-cpp installation
---

### Additional support with Llama-cpp installations for recreating .exe builds with lack of GPU support
- with respect to installing llama-cpp for use in conda environments, follow the following steps for *non cuda-support builds*:
    1. Install latest Visual Studio Build Tools (2019 or 2022)
    2. Activate your conda environment
    3. run `call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"`
    4. verify installations with `where cl` and `where cmake`
    5. run `set CMAKE_ARGS="-DLLAMA_BLAS=OFF -DGGML_CUDA=OFF"`
    6. run `set FORCE_CMAKE=1`
    7. run `set LLAMA_CPP_BUILD_TYPE=cpu`
    8. run `pip install llama-cpp-python --no-cache-dir --verbose`
