import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# 1) Embeddings
emb = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.environ["OPENAI_API_KEY"])

# 2) Vector store (NEW collection if you previously used a different embedding model!)
store = Chroma(
    collection_name="resumes_openai_t3s",
    embedding_function=emb,
    persist_directory="data/chroma_resumes"
)
