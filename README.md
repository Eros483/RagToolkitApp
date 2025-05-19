# RAG Runner

**RAG Runner** is a Retrieval-Augmented Generation (RAG) app that uses a local LLaMA GGUF model. It combines a user-friendly GUI with a backend to fetch context and generate responses, all offline.

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
- Created with CUDA support on LLAMA-CPP. Recreate executable by cloning repository, disabling cuda, and recompiling .exe with `pyinstaller --onefile --windowed rag_gui.py`
---
