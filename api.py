from fastapi import FastAPI
from fastapi.responses import JSONResponse
import chromadb
from pydantic import BaseModel
import chromadb
import requests
from fastapi.middleware.cors import CORSMiddleware


# POST http://localhost:11434/api/embeddings
# {
#   "model": "nomic-embed-text",
#   "prompt": "text to embed"
# }

class QueryRequest(BaseModel):
    question: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sakethmetta.org"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
client = chromadb.PersistentClient(path="/app/database")
collection = client.get_or_create_collection("personal_website_chabot")
response = ""
api = 'http://localhost:11434/api/generate'

@app.post("/response")
def respond(queries: QueryRequest):
    try:
        documents = []
        print(f"The question is: {queries.question}")
        document = collection.query(query_texts=[queries.question], n_results=3)
        print(document)
        for num, dist in enumerate(document["distances"][0]):
            if(dist < 1.5):
                documents.append(document["documents"][0][num])
        print(f"The documents are: {documents}")
        if not documents:
            model_query =   queries.question
            json_object = {"stream": False, "model": "hf.co/bartowski/google_gemma-3-4b-it-qat-GGUF:Q4_K_M",
                            "prompt": model_query}
            response = requests.post(api, json=json_object, timeout=120)
            data = response.json()
            return data.get("response", data.get("error", "No response from model."))

        model_query =   "Query: "+ queries.question + "Information about Saketh: "+ "".join(documents)
        json_object = {"stream": False, "model": "hf.co/bartowski/google_gemma-3-4b-it-qat-GGUF:Q4_K_M",
                        "system": """You are Saketh and answering all the questions that a recruiter is asking in first person.
                        Be concise 2-3 sentences, thats it. Only use the information provided, never invent stuff.
                        If the question is a greeting or small talk, respond naturally without using the retrieved information.""",
                        "prompt": model_query}
        response = requests.post(api, json=json_object, timeout=120)
        print(f"The response is: {response}")
        data = response.json()
        return data.get("response", data.get("error", "No response from model."))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
