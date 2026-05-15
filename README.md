### PersonalLLM — Self-Hosted RAG Chatbot                                                                                                                                                              
                                                                                                                                                                                                   
  A retrieval-augmented generation (RAG) chatbot backend that powers the "ask saketh" widget on sakethmetta.org. Answers questions about my background, research, projects, and skills using a local 
  LLM — no external APIs, no cloud inference.
                                                                                                                                                                                                     
  How It Works                                              

  1. Knowledge base — Plain-text documents in /data cover career goals, education, work experience, technical skills, research, homelab, and projects.                                               
  2. Embedding — chromadb_populate.py embeds each document using nomic-embed-text (via Ollama) and stores them in a persistent ChromaDB collection.
  3. Query — A POST request arrives with a question. The API embeds the question, queries ChromaDB for the top 3 most similar chunks (cosine distance < 1.5), and builds a context-aware prompt.     
  4. Generation — The prompt is sent to qwen2.5:3b running locally via Ollama. The model responds in first person as Saketh, in 2–3 sentences.                                                       
  5. Fallback — If no relevant chunks are found above the similarity threshold, the model answers from its own knowledge without injected context.                                                   
                                                                                                                                                                                                     
  Frontend (sakethmetta.org)                                                                                                                                                                         
          │  POST /response { "question": "..." }                                                                                                                                                    
          ▼                                                                                                                                                                                          
     FastAPI (api.py)
          │  embed question → ChromaDB → top 3 chunks                                                                                                                                                
          │  build prompt                                   
          ▼                                                                                                                                                                                          
     Ollama (localhost:11434)                               
          │  qwen2.5:3b inference                                                                                                                                                                    
          ▼                                                 
     Plain text response → frontend
                                                                                                                                                                                                     
  ---
  Stack                                                                                                                                                                                              
                                                            
  ┌──────────────────┬───────────────────────────┐
  │    Component     │           Tool            │
  ├──────────────────┼───────────────────────────┤
  │ API framework    │ FastAPI + Uvicorn         │
  ├──────────────────┼───────────────────────────┤
  │ LLM inference    │ Ollama (qwen2.5:3b)       │                                                                                                                                                   
  ├──────────────────┼───────────────────────────┤
  │ Embeddings       │ Ollama (nomic-embed-text) │                                                                                                                                                   
  ├──────────────────┼───────────────────────────┤                                                                                                                                                   
  │ Vector database  │ ChromaDB (persistent)     │
  ├──────────────────┼───────────────────────────┤                                                                                                                                                   
  │ Containerization │ Docker                    │          
  ├──────────────────┼───────────────────────────┤
  │ Orchestration    │ k3s (Kubernetes)          │
  ├──────────────────┼───────────────────────────┤
  │ Public exposure  │ Cloudflare Tunnel         │
  └──────────────────┴───────────────────────────┘

  ---
  Project Structure
                                                                                                                                                                                                     
  PersonalLLM/
  ├── api.py                  # FastAPI app — query, retrieve, generate                                                                                                                              
  ├── chromadb_populate.py    # Embeds /data files into ChromaDB
  ├── requirements.txt
  ├── Dockerfile                                                                                                                                                                                     
  ├── chroma_db/              # Persistent ChromaDB storage (generated)
  └── data/                   # Knowledge base (plain text)                                                                                                                                          
      ├── career_goals.txt                                  
      ├── current_projects.txt
      ├── education.txt                                                                                                                                                                              
      ├── homelab.txt
      ├── integrated_portfolio_chatbot.txt                                                                                                                                                           
      ├── postgresql_research.txt                           
      ├── strengths.txt
      ├── suitability_ml.txt
      ├── suitability_robotics.txt                                                                                                                                                                   
      ├── suitability_swe.txt
      ├── technical_skills.txt                                                                                                                                                                       
      └── work_experience.txt                               

  ---                                                                                                                                                                                                
  Prerequisites
                                                                                                                                                                                                     
  - Ollama running locally with models pulled:              
  ollama pull qwen2.5:3b
  ollama pull nomic-embed-text
  - Python 3.12+
  - Docker (for containerized deployment)                                                                                                                                                            
  
  ---                                                                                                                                                                                                
  Setup                                                     

  1. Install dependencies
  pip install -r requirements.txt
                                 
  2. Populate the vector database
                                                                                                                                                                                                     
  Run this whenever you add or update files in /data:
  python chromadb_populate.py                                                                                                                                                                        
                                                            
  3. Run locally
  uvicorn api:app --host 0.0.0.0 --port 8000

  4. Test                                                                                                                                                                                            
  curl -X POST http://localhost:8000/response \
    -H "Content-Type: application/json" \                                                                                                                                                            
    -d '{"question": "What is your research about?"}'       

  ---                                                                                                                                                                                                
  Docker
                                                                                                                                                                                                     
  # Build                                                   
  docker build -t personal-llm .

  # Run
  docker run -p 8000:8000 \
    -v $(pwd)/chroma_db:/app/database \
    --network host \                                                                                                                                                                                 
    personal-llm
                                                                                                                                                                                                     
  ▎ --network host is required so the container can reach Ollama on localhost:11434. The ChromaDB volume mount persists the vector database across restarts.                                         
  
  ---                                                                                                                                                                                                
  Updating the Knowledge Base                               

  1. Edit or add .txt files in /data
  2. Re-run chromadb_populate.py — uses upsert so existing entries update in place
  3. No restart required                                                                                                                                                                             
  
  ---                                                                                                                                                                                                
  API Reference                                             

  POST /response

  Request
  { "question": "string" }

  Response — plain text string.                                                                                                                                                                      
  
  CORS — restricted to https://sakethmetta.org. Update allow_origins in api.py for local development.                                                                                                
                                                            
  ---                                                                                                                                                                                                
  Deployment (k3s)                                          
                  
  Deployed as a Docker container on a 2-node k3s cluster. Ollama runs on the same node (MachineGun) so localhost:11434 resolves correctly via hostNetwork: true. Exposed publicly through Cloudflare
  Tunnel — no inbound ports opened on the home network.   
