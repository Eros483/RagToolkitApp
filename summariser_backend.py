import pymupdf
import llama_cpp
from sentence_transformers import SentenceTransformer
import numpy as np
from PySide6.QtCore import QRunnable, Slot, Signal, QObject
import traceback
import sys
import os
from sklearn.cluster import KMeans

from model_loader import llm_model

model=llm_model

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

def process_files(filepaths: list[str])-> tuple[list[str], np.ndarray]:
    '''
    input: list of filepaths
    processes files for text extraction and embedding
    output: extracted chunks and embeddings
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
        print("Vectorisation succesful")
        return all_chunks, np.vstack(all_vectors)

    else:
        raise ValueError('No text extracted')
def clustering(vectors, num_clusters):
    """
    input: embeddings from given pdf text as vectors
    output: clusters of similar vectors
    """
    if len(vectors)<num_clusters:
        return list(range(len(vectors)))
    
    k=num_clusters
    kmeans=KMeans(n_clusters=k, random_state=42, n_init=10).fit(vectors)
    labels=kmeans.labels_
    closest_indices=[]

    for i in range(num_clusters):
        cluster_indices=np.where(labels==i)[0]
        if len(cluster_indices)>0:
            distances=np.linalg.norm(vectors[cluster_indices]-kmeans.cluster_centers_[i], axis=1)

            closest_index=np.argmin(distances)

            closest_indices.append(cluster_indices[closest_index])

    selected_indices=sorted(list(set(closest_indices)))
    return selected_indices

def summary_creater(selected_indices, chunks):
    """
    input: indices of selected chunks and chunks themselves
    output: summary list of selected chunks
    """
    summary_list=[]
    for i in selected_indices:
        section=chunks[i]
        map_prompt=f"""
        Act as a concise summariser.
        Summarise the given text into 2-3 lines, no more. Ensure you completely cover the content of the text. This text will be enclosed in triple backticks (```)
        The output should be the summary of the user supplied text.
        Be concise and precise in your behaviour.

        ```{section}```
        SUMMARY: 
        """
        temp=0.7
        max_tokens=150

        response=model.create_completion(
        prompt=map_prompt,
        temperature=temp,
        max_tokens=max_tokens
        )

        summary=response['choices'][0]['text']
        summary=summary.replace("[/INST]", "")
        print(summary)
        print(i)
        summary_list.append(summary)
        print(f"Summary for chunk{i} is ready")

    return summary_list

def collate_summaries(individual_summaries: list[str])->str:
    '''
    input: list of individual summaries
    output: summary as a string
    '''
    summaries="\n".join(individual_summaries)
    final_prompt = f"""<|im_start|>system
    You are a precise and concise summariser.
    You will be given a series of summaries from a book. The summaries will be enclosed in triple backticks (```).
    Your task is to write a verbose summary of what was covered in the book.

    The output should be a detailed and coherent summary that captures all the key information present in the provided summaries. Combine each summary into one whole summary 
    The goal is to help a reader understand the entire content of the book from this single collated summary. 

    Do not add any external information. Base your answer only on what is provided. Ensure it is a single stream of text, and not split up. Combine parts to form a bigger whole.
    Capture the sentiment of the book.
    Structure your response in markdown.
    <|im_end|>
    <|im_start|>user
    ```{summaries}```
    Question:
    Provide a detailed summary of the book based on the provided summaries.
    <|im_end|>
    <|im_start|>assistant
    SUMMARY:
    Here is the detailed summary of the book:
    """

    temp=0.7
    max_tokens=3000

    response=model.create_completion(
        prompt=final_prompt,
        temperature=temp,
        max_tokens=max_tokens
    )
    assistant_reply=response['choices'][0]['text']
    collated_summary=assistant_reply.replace("[/INST]", "")
    return collated_summary

class WorkerSignals(QObject):
    finished=Signal()
    error=Signal(str)
    result=Signal(object)

class SummarizationWorker(QRunnable):
    def __init__(self, filepaths: list[str], num_clusters: int=10):
        super().__init__()
        self.filepaths=filepaths
        self.num_clusters=num_clusters
        self.signals=WorkerSignals()
    
    @Slot()
    def run(self):
        try:
            all_chunks, all_vectors=process_files(self.filepaths)
            selected_indices=clustering(all_vectors, self.num_clusters)
            individual_summaries=summary_creater(selected_indices, all_chunks)
            collated_summary=collate_summaries(individual_summaries)
            self.signals.result.emit(collated_summary)
        
        except Exception as e:
            tb=traceback.format_exc()
            self.signals.error.emit(tb)
        finally:
            self.signals.finished.emit()
