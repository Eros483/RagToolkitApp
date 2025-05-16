import pymupdf
import llama_cpp
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from PySide6.QtCore import QRunnable, Slot, Signal, QObject
import traceback

model_path="D:\\personalCode\\ragAgentFitness\\models\\Dolphin3.0-Llama3.2-3B-Q5_K_M.gguf"
llm=llama_cpp.Llama(model_path=model_path, chat_format="llama-2", n_ctx=8192, n_gpu_layers=-1)

index=None
id_to_text={}

embedder=SentenceTransformer('all-MiniLM-L6-v2')

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
    
def ask_model(question: str)->str:
    '''
    input: question as a string
    output: answer as a string
    '''
    context="\n\n".join(search_chunks(question))

    final_prompt=f"""<|im_start|>system
    You are a helpful assistant. If the answer is not present in the context, print "Insufficient context" and nothing else. Structure your response in markdown, using bullet points or headings if appropriate. Ensure that if there is no relevant information, you provide "Insufficient context" and nothing else at all. <|im_end|>
    <|im_start|>user
    Use the following context to answer the question.

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
    result=Signal(str)

class RAGWorker(QRunnable):
    def __init__(self, filepaths, question=None):
        super().__init__()
        self.filepaths=filepaths
        self.question=question
        self.signals=WorkerSignals()
    
    @Slot()
    def run(self):
        try:
            process_files(self.filepaths)
            if self.question:
                result=ask_model(self.question)
                self.signals.result.emit(result)
        
        except Exception as e:
            tb=traceback.format_exc()
            self.signals.error.emit(tb)
        finally:
            self.signals.finished.emit()