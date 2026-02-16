from fastapi import FastAPI, HTTPException, UploadFile, File
from app.ingestion import process_documents
from app.retrieval import retrieve
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Continuous RAG - Bulletproof")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("MODEL", "mixtral-8x7b-32768")


@app.get("/")
def root():
    return {
        "status": "online",
        "title": "Continuous RAG - Bulletproof Version Detection",
        "description": "Automatically uses latest document versions only",
        "endpoints": {
            "POST /upload": "Upload a new PDF",
            "GET /update": "Index documents (auto cleanup)",
            "GET /query?q=question": "Ask a question",
            "GET /status": "Check indexed files"
        }
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    os.makedirs("documents", exist_ok=True)
    filepath = os.path.join("documents", file.filename)
    
    try:
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "status": "uploaded",
            "filename": file.filename,
            "next_step": "Call GET /update to index this document"
        }
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")


@app.get("/update")
def update_documents():
    """
    Index documents with automatic cleanup.
    ALWAYS does fresh rebuild to guarantee only latest versions.
    """
    try:
        result = process_documents()
        return result
    except Exception as e:
        raise HTTPException(500, f"Indexing failed: {str(e)}")


@app.get("/query")
def query(q: str, top_k: int = 3):
    """
    Query the knowledge base.
    Returns answers from latest document versions only.
    """
    if not q or not q.strip():
        raise HTTPException(400, "Query parameter 'q' required")
    
    try:
        # Retrieve relevant chunks
        contexts = retrieve(q, top_k=top_k)
        
        if not contexts:
            return {
                "answer": "No information found. Please upload documents and call /update",
                "sources": [],
                "query": q
            }
        
        # Build prompt
        context_text = "\n\n".join([
            f"[Source: {c['filename']}]\n{c['text']}"
            for c in contexts
        ])
        
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the context below.
Do not mention version numbers or multiple versions.
If the context doesn't answer the question, say "I don't have enough information."

Context:
{context_text}

Question: {q}

Answer (be concise and direct):"""
        
        # Get LLM response
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "sources": [{"filename": c["filename"], "version": c["version"]} for c in contexts],
            "query": q,
            "num_sources": len(contexts)
        }
        
    except Exception as e:
        raise HTTPException(500, f"Query failed: {str(e)}")


@app.get("/status")
def status():
    """Check which documents are currently indexed"""
    from app.database import cursor
    
    cursor.execute("SELECT filename, version FROM documents ORDER BY filename")
    docs = cursor.fetchall()
    
    return {
        "total_documents": len(docs),
        "indexed_files": [{"filename": d[0], "version": d[1]} for d in docs]
    }
