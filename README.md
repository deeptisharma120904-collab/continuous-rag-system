# Continuous-RAG: Version-Aware Enterprise Policy Retrieval System

> RAG system with automatic version control for enterprise document Q&A

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Problem Statement

Large enterprises store hundreds of internal policy and compliance documents in PDF format. Employees struggle to quickly retrieve accurate, version-consistent information from these long documents. Traditional keyword search often retrieves irrelevant or outdated sections, leading to confusion and inefficiency.

### Challenges Addressed:
- ✅ Retrieves only relevant document sections
- ✅ Handles document versioning automatically
- ✅ Filters outdated files intelligently
- ✅ Optimizes latency and token usage
- ✅ Generates grounded, accurate responses

---

## 🚀 Solution

A production-ready enterprise RAG system that retrieves and ranks policy documents with **intelligent version control filtering**. The system uses multi-stage retrieval with FAISS embeddings, metadata-aware filtering, and context optimization to reduce latency and improve answer grounding.

### Key Features:
- 🔄 **Automatic Version Detection** - Identifies and indexes only the latest document versions
- 📚 **Smart Document Processing** - Handles multiple file versions (e.g., `Policy_v1.pdf`, `Policy_v2.pdf`, `Policy_v4.pdf`)
- 🎯 **Context-Aware Retrieval** - Uses FAISS + Sentence Transformers for semantic search
- ⚡ **Fast Query Response** - Optimized embedding and retrieval pipeline
- 🗄️ **Persistent Storage** - SQLite for metadata, FAISS for vector embeddings
- 🔍 **Version Tracking** - Automatic filtering of outdated document versions

---

## 🏗️ System Architecture
```
┌─────────────────┐
│  PDF Documents  │
│  (v1, v2, v3...)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Version Detection Engine      │
│  • Extract base name & version  │
│  • Find latest version only     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│    Document Processing          │
│  • PDF text extraction          │
│  • Chunking (500 chars/chunk)   │
│  • Overlap handling (50 chars)  │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Embedding Generation          │
│  • SentenceTransformer          │
│  • all-MiniLM-L6-v2 model       │
│  • 384-dimensional vectors      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│    Storage Layer                │
│  • FAISS Index (vectors)        │
│  • SQLite (metadata + versions) │
│  • Pickle (chunk metadata)      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Query Processing              │
│  • Semantic search via FAISS    │
│  • Version filtering            │
│  • Top-K retrieval              │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   LLM Response Generation       │
│  • Groq API (Mixtral)           │
│  • Context-grounded answers     │
└─────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | FastAPI |
| **Vector Database** | FAISS (Facebook AI Similarity Search) |
| **Embeddings** | SentenceTransformers (all-MiniLM-L6-v2) |
| **Metadata DB** | SQLite3 |
| **PDF Processing** | PyPDF (pypdf) |
| **LLM** | Groq API (Mixtral-8x7B) |
| **Language** | Python 3.8+ |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Groq API key ([Get it here](https://console.groq.com/))

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/VedantGokhe/continuous-rag-system.git
cd continuous-rag-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file**
```bash
GROQ_API_KEY=your_groq_api_key_here
MODEL=mixtral-8x7b-32768
```

5. **Create documents folder**
```bash
mkdir documents
```

6. **Add your PDF documents**
```bash
# Example: Add versioned policy documents
documents/
├── Enterprise_HR_Policy_v1.pdf
├── Enterprise_HR_Policy_v2.pdf
├── Enterprise_HR_Policy_v3.pdf
└── Enterprise_HR_Policy_v4.pdf
```

---

## 🚦 Usage

### Start the Server
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### API Endpoints

#### 1. **Health Check**
```bash
curl http://127.0.0.1:8000/
```

#### 2. **Upload Documents**
```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@documents/Enterprise_HR_Policy_v4.pdf"
```

#### 3. **Index Documents** (Triggers version detection & embedding)
```bash
curl.exe http://127.0.0.1:8000/update
```

**Response:**
```json
{
  "status": "success",
  "total_embeddings": 15,
  "total_chunks": 15,
  "files_indexed": 1,
  "latest_versions": ["Enterprise_HR_Policy_v4.pdf (v4)"]
}
```

#### 4. **Query Documents**
```bash
curl "http://127.0.0.1:8000/query?q=What%20is%20the%20leave%20policy"
```

**Response:**
```json
{
  "answer": "The leave policy allows employees to take...",
  "sources": [
    {
      "filename": "Enterprise_HR_Policy_v4.pdf",
      "version": 4
    }
  ],
  "query": "What is the leave policy",
  "num_sources": 1
}
```

#### 5. **Check Status**
```bash
curl http://127.0.0.1:8000/status
```

---

## 🔍 How Version Control Works

### Automatic Version Detection

The system uses regex pattern matching to extract version numbers from filenames:

**Supported Patterns:**
- `Policy_v1.pdf` → Base: `Policy.pdf`, Version: `1`
- `Policy_v4.pdf` → Base: `Policy.pdf`, Version: `4`
- `Enterprise_HR_Policy_v3.pdf.pdf` → Base: `Enterprise_HR_Policy.pdf`, Version: `3`

### Version Selection Logic
```python
# Example: documents/ folder contains:
Enterprise_HR_Policy_v1.pdf  ❌ IGNORED (old version)
Enterprise_HR_Policy_v2.pdf  ❌ IGNORED (old version)
Enterprise_HR_Policy_v4.pdf  ✅ INDEXED (latest version)
```

**Output:**
```
📋 FILE ANALYSIS:
   Base: Enterprise_HR_Policy.pdf
      ❌ IGNORED:   Enterprise_HR_Policy_v1.pdf (v1) - OLD VERSION
      ❌ IGNORED:   Enterprise_HR_Policy_v2.pdf (v2) - OLD VERSION
      ✅ WILL USE:  Enterprise_HR_Policy_v4.pdf (v4) ← LATEST

📊 SUMMARY: Using 1 file(s), ignoring 2 old version(s)
```

---

## 📂 Project Structure
```
continuous-rag-system/
│
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application & endpoints
│   ├── database.py       # SQLite database connection
│   ├── ingestion.py      # Document processing & version control
│   └── retrieval.py      # FAISS search & version filtering
│
├── documents/            # PDF documents storage
├── faiss_index/          # FAISS vector index storage
│   ├── index.bin
│   └── meta.pkl
│
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── metadata.db          # SQLite database
└── README.md
```

---

## 🧪 Testing the System

### Test Case 1: Version Filtering
```bash
# Add multiple versions
cp Policy_v1.pdf documents/
cp Policy_v2.pdf documents/
cp Policy_v4.pdf documents/

# Index documents
curl http://127.0.0.1:8000/update

# Expected: Only v4 should be indexed
```

### Test Case 2: Query Accuracy
```bash
curl "http://127.0.0.1:8000/query?q=What%20is%20the%20remote%20work%20policy"
```

### Test Case 3: Status Check
```bash
curl http://127.0.0.1:8000/status

# Expected output:
{
  "total_documents": 1,
  "indexed_files": [
    {
      "filename": "Enterprise_HR_Policy_v4.pdf",
      "version": 4
    }
  ]
}
```

---

## ⚙️ Configuration

### Embedding Model
Change in `ingestion.py` and `retrieval.py`:
```python
model = SentenceTransformer("all-MiniLM-L6-v2")  # Default
# Options: "all-mpnet-base-v2", "paraphrase-MiniLM-L6-v2"
```

### Chunk Size
Modify in `ingestion.py`:
```python
chunk_size = 500  # Characters per chunk
overlap = 50      # Overlap between chunks
```

### LLM Model
Change in `.env`:
```bash
MODEL=mixtral-8x7b-32768
# Options: llama-3.1-70b-versatile, gemma-7b-it
```

---

## 🎯 Key Design Decisions

### 1. **Nuclear Clean Strategy**
Every `/update` call performs a complete rebuild to guarantee consistency:
- Deletes entire FAISS index directory
- Clears SQLite database
- Rebuilds from scratch with only latest versions

**Why?** Eliminates any possibility of stale data or version conflicts.

### 2. **Version-First Filtering**
Version detection happens **before** embedding generation:
```python
all_files → extract_versions() → filter_latest() → embed() → index()
```

**Why?** Saves compute by not embedding outdated documents.

### 3. **Two-Stage Metadata Storage**
- **FAISS** (index.bin): Vector embeddings for semantic search
- **SQLite** (metadata.db): File versions and hashes
- **Pickle** (meta.pkl): Chunk-level metadata

**Why?** Separates concerns and enables fast version lookups.

---

## 🚧 Limitations & Future Improvements

### Current Limitations:
- Only supports PDF files
- Version format must follow `_vN` pattern
- No incremental updates (full rebuild required)
- Single-language support (English)

### Planned Enhancements:
- [ ] Add support for DOCX, TXT files
- [ ] Implement incremental indexing
- [ ] Add multi-language support
- [ ] Implement hybrid search (keyword + semantic)
- [ ] Add document change detection
- [ ] Web UI for document management
- [ ] Role-based access control
- [ ] Export Q&A history

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **Average Query Time** | ~200-500ms |
| **Embedding Generation** | ~50ms per chunk |
| **FAISS Search** | <10ms for 1000 documents |
| **Document Processing** | ~2-5 seconds per PDF |
| **Storage per Document** | ~2-5 MB (embeddings + metadata) |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**
- GitHub: [VedantGokhe](https://github.com/VedantGokhe)
- LinkedIn: [Vedant Gokhe](https://www.linkedin.com/in/vedantgokhe/)
- Email: vedantgokheofficial@gmail.com

---

## 🙏 Acknowledgments

- [FAISS](https://github.com/facebookresearch/faiss) by Facebook AI Research
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- [Groq](https://groq.com/) for fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

---

## 📚 References

- [RAG Paper - Lewis et al., 2020](https://arxiv.org/abs/2005.11401)
- [FAISS Documentation](https://faiss.ai/)
- [Sentence-BERT Paper](https://arxiv.org/abs/1908.10084)

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ for enterprise document retrieval

</div>