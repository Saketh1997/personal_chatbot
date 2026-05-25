import chromadb
import os
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

embedding_fn = OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text"
)

client = chromadb.PersistentClient(path="/home/hunter/projects/LLM_Projects/PersonalLLM/chroma_db")
collection = client.get_or_create_collection("personal_website_chabot", embedding_function=embedding_fn)

for dirpath, dirnames, filenames in os.walk("/home/hunter/projects/LLM_Projects/PersonalLLM/data"):
    for file in filenames:
        with open(os.path.join(dirpath, file), "r") as f:
            content = f.read()
            collection.upsert(
                documents=[content],
                ids=[file]
            )
            print(f"Upserted: {file}")
