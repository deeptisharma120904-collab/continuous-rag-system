# Continuous-RAG: Version-Aware Enterprise Policy Retrieval System

> RAG system with automatic document detection and version control for enterprise document Q&A

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Problem Statement

Large enterprises store hundreds of internal policy and compliance documents in PDF format. Employees struggle to quickly retrieve accurate, version-consistent information from these long documents. Traditional keyword search often retrieves irrelevant or outdated sections, leading to confusion and inefficiency.

### Challenges Addressed:
- ✅ Retrieves only relevant document sections
- ✅ Automatically detects and processes any new document uploaded
- ✅ Filters outdated files intelligently
- ✅ Optimizes latency and token usage
- ✅ Generates grounded, accurate responses

---

## 🚀 Solution

A production-ready enterprise RAG system that retrieves and ranks policy documents with **intelligent auto-detection and version control filtering**. The system uses multi-stage retrieval with FAISS embeddings, metadata-aware filtering, and context optimization to reduce latency and improve answer grounding.

### Key Features:
- 🔄 **Automatic Document Detection** - Any new document uploaded is automatically detected and indexed — no manual version tagging required
- 📚 **Smart Document Processing** - Handles any PDF file regardless of naming convention
- 🎯 **Context-Aware Retrieval** - Uses FAISS + Sentence Transformers for semantic search
- ⚡ **Fast Query Response** - Optimized embedding and retrieval pipeline
- 🗄️ **Persistent Storage** - SQLite for metadata, FAISS for vector embeddings
- 🔍 **Version Tracking** - Automatic filtering of outdated document versions

---

## 🏗️ System Architecture
```
┌─────────────────┐
│  PDF Documents  │
│  (any filename) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Auto Detection Engine         │
│  • Detects any new document     │
│  • No version tag required      │
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
git clone https://github.com/deeptisharma120904-collab/continuous-rag-system.git
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
# Example: Add any policy documents — no special naming needed
documents/
├── HR_Policy.pdf
├── Finance_Guidelines.pdf
└── Compliance_Rules.pdf
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
  -F "file=@documents/HR_Policy.pdf"
```

#### 3. **Index Documents** (Triggers auto detection & embedding)
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
  "latest_versions": ["HR_Policy.pdf (v1)"]
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
      "filename": "HR_Policy.pdf",
      "version": 1
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

## 🔍 How Auto Detection Works

### Automatic Document Detection

The system automatically detects and indexes any new PDF uploaded — no special naming convention or version tag required.

**How it works:**
- Upload any PDF → system detects it automatically
- Call `/update` → fresh index is built instantly
- Query immediately → answers from the latest uploaded documents

### Optional Version Support
If you do use versioned filenames, the system still handles them:
- `Policy_v1.pdf` → Base: `Policy.pdf`, Version: `1`
- `Policy_v4.pdf` → Base: `Policy.pdf`, Version: `4` ← automatically preferred

---

## 📂 Project Structure
```
continuous-rag-system/
│
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application & endpoints
│   ├── database.py       # SQLite database connection
│   ├── ingestion.py      # Document processing & auto detection
│   └── retrieval.py      # FAISS search & version filtering
│
├── documents/            # PDF documents storage
├── faiss_index/          # FAISS vector index storage
│   ├── index.bin
│   └── meta.pkl
│
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── metadata.db           # SQLite database
└── README.md
```

---

## 🧪 Testing the System

### Test Case 1: Auto Detection
```bash
# Add any PDF — no version naming needed
cp my_policy.pdf documents/

# Index documents
curl http://127.0.0.1:8000/update

# Expected: Document automatically detected and indexed
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
      "filename": "HR_Policy.pdf",
      "version": 1
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
- Rebuilds from scratch with only the latest documents

**Why?** Eliminates any possibility of stale data or version conflicts.

### 2. **Auto Detection First**
Document detection happens **before** embedding generation:
```python
all_files → auto_detect() → filter_latest() → embed() → index()
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

**Deepti Sharma**
- GitHub: [deeptisharma120904-collab](https://github.com/deeptisharma120904-collab)
- LinkedIn: [Deepti Sharma](https://www.linkedin.com/in/deepti-sharma-208aaa2b9/)
- Email: deepti.sharma120904@gmail.com

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
