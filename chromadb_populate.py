import chromadb
import os

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("personal_website_chabot")

for dirpath, dirnames, filenames in os.walk("/home/hunter/LLM_Projects/PersonalLLM/data"):
    for file in filenames:
        with open(os.path.join(dirpath, file), "r") as f:
            content = f.read()
            collection.upsert(
                documents=[content],
                ids=[file]
            )
            print(f"Upserted: {file}")
