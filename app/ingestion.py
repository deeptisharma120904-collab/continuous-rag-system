import os
import hashlib
import faiss
import pickle
import re
import shutil
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from app.database import conn, cursor

model = SentenceTransformer("all-MiniLM-L6-v2")

# Storage paths
if os.path.exists("/opt/render/project/src/data"):
    BASE_DIR = "/opt/render/project/src/data"
else:
    BASE_DIR = "."

INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")
INDEX_PATH = os.path.join(INDEX_DIR, "index.bin")
META_PATH = os.path.join(INDEX_DIR, "meta.pkl")


def get_file_hash(filepath):
    """Calculate file hash"""
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def extract_base_name_and_version(filename):
    """
    Extract base filename and version number.
    Handles multiple patterns:
    - 'Policy_v4.pdf' -> ('Policy.pdf', 4)
    - 'Policy_v4.pdf.pdf' -> ('Policy.pdf', 4)
    - 'Enterprise_HR_Policy_v3.pdf.pdf' -> ('Enterprise_HR_Policy.pdf', 3)
    """
    # Remove .pdf.pdf if present
    clean_name = filename
    if filename.endswith('.pdf.pdf'):
        clean_name = filename[:-4]  # Remove one .pdf
    
    # Pattern to match version number
    pattern = r'^(.+?)_v(\d+)(\.pdf)$'
    match = re.match(pattern, clean_name)
    
    if match:
        base_name = match.group(1) + match.group(3)
        version_num = int(match.group(2))
        return base_name, version_num
    
    # No version found - treat as version 1
    return clean_name, 1


def get_latest_version_files(files):
    """
    Return only the highest version of each document.
    Example: ['Policy_v1.pdf', 'Policy_v2.pdf', 'Policy_v4.pdf'] 
    Returns: {'Policy.pdf': ('Policy_v4.pdf', 4)}
    """
    file_versions = {}
    
    for file in files:
        if not file.endswith('.pdf'):
            continue
            
        base_name, version = extract_base_name_and_version(file)
        
        if base_name not in file_versions:
            file_versions[base_name] = {'file': file, 'version': version}
        else:
            if version > file_versions[base_name]['version']:
                file_versions[base_name] = {'file': file, 'version': version}
    
    return {base: (info['file'], info['version']) for base, info in file_versions.items()}


def nuclear_clean():
    """
    NUCLEAR OPTION: Delete EVERYTHING and start fresh.
    This guarantees no old data remains.
    """
    print("\n" + "="*80)
    print("💣 NUCLEAR CLEAN - DELETING ALL OLD DATA")
    print("="*80)
    
    # Delete entire faiss_index directory
    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)
        print(f"   ✅ Deleted entire directory: {INDEX_DIR}")
    
    # Recreate empty directory
    os.makedirs(INDEX_DIR, exist_ok=True)
    print(f"   ✅ Created fresh directory: {INDEX_DIR}")
    
    # Delete all records from database
    cursor.execute("DELETE FROM documents")
    conn.commit()
    print("   ✅ Wiped database clean")
    
    print("="*80)


def process_documents():
    """
    BULLETPROOF processing:
    1. ALWAYS do nuclear clean first
    2. Find latest versions only
    3. Build fresh index from scratch
    4. Save to fresh files
    """
    
    print("\n" + "🚀"*40)
    print("BULLETPROOF CONTINUOUS RAG - GUARANTEED FRESH BUILD")
    print("🚀"*40 + "\n")
    
    # Get all PDF files
    if not os.path.exists("documents"):
        print("❌ ERROR: documents/ folder not found")
        return {"status": "error", "message": "No documents folder"}
    
    all_files = [f for f in os.listdir("documents") if f.endswith('.pdf')]
    
    if not all_files:
        print("❌ ERROR: No PDF files found in documents/")
        return {"status": "error", "message": "No PDF files"}
    
    print(f"📂 Found {len(all_files)} PDF file(s) in documents/\n")
    
    # Get only latest versions
    latest_files = get_latest_version_files(all_files)
    
    print("📋 FILE ANALYSIS:")
    print("-" * 80)
    
    # Show all files with their status
    files_by_base = {}
    for file in all_files:
        base_name, version = extract_base_name_and_version(file)
        if base_name not in files_by_base:
            files_by_base[base_name] = []
        files_by_base[base_name].append((file, version))
    
    for base_name in sorted(files_by_base.keys()):
        print(f"\n   Base: {base_name}")
        file_list = sorted(files_by_base[base_name], key=lambda x: x[1])
        for file, version in file_list:
            latest_file, latest_version = latest_files[base_name]
            if file == latest_file:
                print(f"      ✅ WILL USE:  {file:45} (v{version}) ← LATEST")
            else:
                print(f"      ❌ IGNORED:   {file:45} (v{version}) - OLD VERSION")
    
    print("-" * 80)
    print(f"\n📊 SUMMARY: Using {len(latest_files)} file(s), ignoring {len(all_files) - len(latest_files)} old version(s)\n")
    
    # STEP 1: NUCLEAR CLEAN (always!)
    nuclear_clean()
    
    # STEP 2: BUILD FRESH INDEX
    print("\n" + "="*80)
    print("🔨 BUILDING FRESH INDEX FROM SCRATCH")
    print("="*80 + "\n")
    
    index = faiss.IndexFlatL2(384)
    metadata = []
    
    for base_name, (filename, version) in latest_files.items():
        filepath = os.path.join("documents", filename)
        
        print(f"📄 Processing: {filename} (v{version})")
        
        try:
            # Read PDF
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
            
            if not text.strip():
                print(f"   ⚠️  No text extracted - skipping")
                continue
            
            # Create chunks
            chunk_size = 500
            overlap = 50
            chunks = []
            
            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i:i + chunk_size].strip()
                if chunk:
                    chunks.append(chunk)
            
            if not chunks:
                print(f"   ⚠️  No chunks created - skipping")
                continue
            
            print(f"   📦 Created {len(chunks)} chunks")
            
            # Generate embeddings
            print(f"   🧠 Generating embeddings...")
            embeddings = model.encode(chunks)
            
            # Add to index
            start_idx = index.ntotal
            index.add(embeddings)
            
            # Save metadata with actual version number
            for i, chunk in enumerate(chunks):
                metadata.append({
                    "filename": filename,
                    "base_name": base_name,
                    "text": chunk,
                    "version": version,
                    "chunk_id": i
                })
            
            # Save to database with actual version number
            file_hash = get_file_hash(filepath)
            cursor.execute(
                "INSERT INTO documents (filename, file_hash, version) VALUES (?, ?, ?)",
                (filename, file_hash, version)
            )
            conn.commit()
            
            print(f"   ✅ Successfully indexed {len(chunks)} chunks (version {version})\n")
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}\n")
            continue
    
    # STEP 3: SAVE TO FRESH FILES
    print("="*80)
    print("💾 SAVING INDEX AND METADATA")
    print("="*80)
    
    # Save FAISS index
    faiss.write_index(index, INDEX_PATH)
    print(f"   ✅ Saved index: {INDEX_PATH}")
    
    # Save metadata
    with open(META_PATH, "wb") as f:
        pickle.dump(metadata, f)
    print(f"   ✅ Saved metadata: {META_PATH}")
    
    print("\n" + "="*80)
    print("✅ BUILD COMPLETE")
    print("="*80)
    print(f"   • Total embeddings: {index.ntotal}")
    print(f"   • Total chunks: {len(metadata)}")
    print(f"   • Files indexed: {len(latest_files)}")
    
    # Show which versions were indexed
    versions_info = [f"{filename} (v{version})" for base, (filename, version) in latest_files.items()]
    print(f"   • Latest versions indexed:")
    for info in sorted(versions_info):
        print(f"      - {info}")
    
    print("="*80 + "\n")
    
    return {
        "status": "success",
        "total_embeddings": index.ntotal,
        "total_chunks": len(metadata),
        "files_indexed": len(latest_files),
        "latest_versions": [f"{filename} (v{version})" for base, (filename, version) in latest_files.items()]
    }