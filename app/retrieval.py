import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from app.database import cursor

model = SentenceTransformer("all-MiniLM-L6-v2")

# Storage paths
if os.path.exists("/opt/render/project/src/data"):
    BASE_DIR = "/opt/render/project/src/data"
else:
    BASE_DIR = "."

INDEX_PATH = os.path.join(BASE_DIR, "faiss_index", "index.bin")
META_PATH = os.path.join(BASE_DIR, "faiss_index", "meta.pkl")


def retrieve(query, top_k=5):
    """
    Retrieve chunks for query.
    ONLY returns results from files currently in database.
    Always uses the LATEST version of each document.
    """
    
    # Load index and metadata
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        print("⚠️  No index found. Call /update first.")
        return []
    
    index = faiss.read_index(INDEX_PATH)
    
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)
    
    if not metadata:
        print("⚠️  No metadata found.")
        return []
    
    # Get currently indexed files from database
    cursor.execute("SELECT filename FROM documents")
    db_files = {row[0] for row in cursor.fetchall()}
    
    if not db_files:
        print("⚠️  No files in database.")
        return []
    
    # Find latest version for each base_name
    latest_versions = {}
    for chunk in metadata:
        filename = chunk["filename"]
        if filename in db_files:
            base_name = chunk.get("base_name", filename)
            version = chunk.get("version", 1)
            
            if base_name not in latest_versions or version > latest_versions[base_name]:
                latest_versions[base_name] = version
    
    print(f"\n🔍 RETRIEVAL DEBUG:")
    print(f"   • Files in database: {db_files}")
    print(f"   • Total metadata chunks: {len(metadata)}")
    print(f"   • Latest versions: {latest_versions}")
    
    # Get query embedding
    query_vector = model.encode([query])
    
    # Search
    search_k = min(top_k * 10, len(metadata))
    distances, indices = index.search(query_vector, search_k)
    
    results = []
    seen_bases = set()
    
    for idx, distance in zip(indices[0], distances[0]):
        if idx >= len(metadata):
            continue
        
        chunk = metadata[idx]
        filename = chunk["filename"]
        base_name = chunk.get("base_name", filename)
        version = chunk.get("version", 1)
        
        # CRITICAL: Only include if file is in database AND it's the latest version
        if filename in db_files:
            if base_name in latest_versions and version == latest_versions[base_name]:
                if base_name not in seen_bases:
                    results.append({
                        "filename": filename,
                        "base_name": base_name,
                        "text": chunk["text"],
                        "version": version,
                        "distance": float(distance),
                        "chunk_id": chunk.get("chunk_id", 0)
                    })
                    seen_bases.add(base_name)
                    
                    if len(results) >= top_k:
                        break
    
    print(f"   • Results found: {len(results)}")
    if results:
        print(f"   • Source files: {[r['filename'] for r in results]}")
    print()
    
    return results