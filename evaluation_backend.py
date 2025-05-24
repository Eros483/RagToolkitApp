import pymupdf
import llama_cpp
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from PySide6.QtCore import QRunnable, Slot, Signal, QObject
import traceback
import sys
import os
import json

if getattr(sys, 'frozen', False):
    # Running as a bundled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as a .py file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from model_loader import llm_model

llm=llm_model


json_path=os.path.join(BASE_DIR, "sample_json", "sample1.json")

if not os.path.exists(json_path):
    raise ValueError(f"Model path or json path does not exist: {json_path}")

index=None
id_to_text={}

embedder=SentenceTransformer('all-MiniLM-L6-v2')

def extract_json_information(filepath: str)->dict:
    '''
    input: path of json file
    output: infomration contained in the given json
    '''
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def split_into_chunks(text, chunk_size=500, overlap=50):
    '''
    input: text in the form of  a string
    output: list of chunks of text, each of size chunk_size
    '''
    
    chunks=[]
    for i in range(0, len(text), chunk_size-overlap):
        chunks.append(text[i:i+chunk_size])
    return chunks

def embed_text(text:str)->np.ndarray:
    # embed the text using the sentence transformer model
    '''
    input: text in the form of a string
    output: embedding of the text in the form of a numpy array
    '''

    chunks=split_into_chunks(text)
    vectors=embedder.encode(chunks)
    return chunks, vectors

def extract_text_from_pdf(filepath: str)-> str:
    '''
    input: filepath of pdf
    output: text extracted from the pdf
    '''
    doc=pymupdf.open(filepath)
    full_text=""
    for page in doc:
        full_text+=page.get_text()
    return full_text

def create_index(vectors, chunks):
    '''
    input: list of vectors and list of chunks
    output: faiss index
    '''
    global index
    global id_to_text
    dimension=vectors.shape[1]
    index=faiss.IndexFlatL2(dimension)
    index.reset()
    index.add(np.array(vectors).astype('float32'))
    id_to_text={i:text for i,text in enumerate(chunks)}

def search_chunks(query, top_k=3):
    '''
    input: query in the form of a string
    output: top_k most similar chunks
    '''
    query_vec=embedder.encode([query]).astype('float32')
    D, I = index.search(query_vec, k=top_k)
    return [id_to_text[i] for i in I[0]]

def process_files(filepaths: list[str])-> None:
    '''
    input: list of filepaths
    processes files for text extraction and embedding
    output: None
    '''
    all_chunks=[]
    all_vectors=[]
    for path in filepaths:
        if path.endswith('.pdf'):
            text=extract_text_from_pdf(path)

        elif path.endswith('.json'):
            with open(path, 'r') as f:
                text=f.read()
        
        else:
            continue
        chunks, vectors=embed_text(text)
        all_chunks.extend(chunks)
        all_vectors.append(vectors)

    if all_vectors:
        all_vectors=np.vstack(all_vectors)
        create_index(all_vectors, all_chunks)

    else:
        raise ValueError('No text extracted')
    
def ask_model(question: str, history: list[tuple[str, str]], json_path: str)->str:
    '''
    input: question as a string, and history of previous questions and answers
    output: answer as a string
    '''
    context="\n\n".join(search_chunks(question))

    metrics=extract_json_information(json_path)

    chat_history=""
    for q,a in history:
        chat_history+="Q: "+q+"\nA: "+a+"\n\n"

    final_prompt=f"""<|im_start|>system
    You are a helpful assistant in a document Q&A app set up, where the task is to generate evaluation feedback. Consider the metrics to contain information on the conducted evaluation. Use the added context, to enhance the answers created from the metrics. If the answer is not present in the context, print "Insufficient context" and nothing else. Structure your response in markdown, using bullet points or headings if appropriate. Ensure that if there is no relevant information, you provide "Insufficient context" and nothing else at all. <|im_end|>
    {chat_history}
    <|im_start|>user
    Use the following metrics to answer the question. Enhance the answer using the given context, and print only the answer in markdown. Do not print information irrelevant to the question. If information is present in the context, do not print anything about insufficient context.

    Metrics:
    {metrics}

    Context:
    {context}

    Question:
    {question}<|im_end|>
    <|im_start|>assistant
    """

    temp=0.7
    max_tokens=512

    response=llm.create_completion(
        prompt=final_prompt,
        temperature=temp,
        max_tokens=max_tokens
    )

    assistant_reply=response['choices'][0]['text']
    assistant_reply=assistant_reply.replace("[/INST]", "")
    return assistant_reply

class WorkerSignals(QObject):
    finished=Signal()
    error=Signal(str)
    result=Signal(object)

class EvaluationWorker(QRunnable):
    def __init__(self, filepaths, json_filepath, question=None, history=None):
        super().__init__()
        self.filepaths=filepaths
        self.json_filepath=json_filepath
        self.question=question
        self.history=history or []
        self.signals=WorkerSignals()
    
    @Slot()
    def run(self):
        try:
            process_files(self.filepaths)
            if self.question:
                result=ask_model(self.question, self.history, self.json_filepath)
                self.history.append((self.question, result))
                self.signals.result.emit((result, self.history))
        
        except Exception as e:
            tb=traceback.format_exc()
            self.signals.error.emit(tb)
        finally:
            self.signals.finished.emit()
