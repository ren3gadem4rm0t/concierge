from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os
import weaviate
import json
import requests

# variables
source_path = '/home/douglas/All_SANS_Classes/'


source_files = os.listdir(source_path)
chunk_size = 200
chunk_overlap = 25

stransform = SentenceTransformer('paraphrase-MiniLM-L6-v2')

splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap
)

client = weaviate.Client(
    url = "http://127.0.0.1:8080"
)

class_obj = {
    "class": "Fact",
    "properties": [
        {
            "name": "metadata",
            "dataType": ["text"],
        },
        {
            "name": "text",
            "dataType": ["text"],
        },
    ],
}

def VectorizePDF(pdf):
    loader = PyPDFLoader(f'{source_path}{pdf}')
    pages = loader.load_and_split()
    PageProgress = tqdm(total=len(pages))
    for page in pages:
        PageProgress.update(1)
        metadata = page.metadata
        chunks = splitter.split_text(page.page_content)
        for chunk in chunks:
            vect = stransform.encode(chunk)

            client.data_object.create(class_name="Fact",
                                      data_object={
                                          "metadata":str(f"Page {metadata['page']+1} of {pdf}"),
                                          "text":chunk,
                                          },
                                          vector = vect
            )


client.schema.create_class(class_obj) 

for pdf in source_files:
    print(pdf)
    VectorizePDF(pdf)
