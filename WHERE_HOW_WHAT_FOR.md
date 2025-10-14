# Where, How, and What Is Being Installed

## 📍 WHERE Is This Installing?

### Location: Inside Docker Containers (Isolated Virtual Environments)

```
Your Computer (Windows)
│
├─ Windows Files (C:\Users\...)
│  └─ Your project folder ← Just scripts and config files
│
└─ WSL2 (Ubuntu Linux)
   └─ Docker Engine
      └─ CONTAINERS ← THIS IS WHERE EVERYTHING INSTALLS
         │
         ├─ Backend Container (~3GB)
         │  ├─ Ubuntu 22.04
         │  ├─ CUDA 12.6
         │  ├─ Python 3.11
         │  ├─ PyTorch (AI library)
         │  └─ Your backend code
         │
         ├─ Frontend Container (~500MB)
         │  ├─ Node.js
         │  ├─ React
         │  └─ Your frontend code
         │
         ├─ Database Container (~200MB)
         │  └─ PostgreSQL
         │
         ├─ Storage Container (~100MB)
         │  └─ MinIO
         │
         └─ Search Container (~600MB)
            └─ OpenSearch
```

### Important Points:

**NOT on your Windows drive directly**
- Installation happens in isolated containers
- Like virtual machines, but lighter
- Each container has its own filesystem

**Storage Location (Docker):**
```
Physical location on disk:
C:\Users\<you>\AppData\Local\Docker\wsl\data\

But you don't need to worry about this!
Docker manages it automatically.
```

**Your Project Files Stay Clean:**
```
Your folder only contains:
- Source code
- Configuration files (docker-compose.yml)
- Scripts (.ps1, .sh)
- Documentation (.md files)

NOT:
- ❌ Installed packages
- ❌ Python libraries
- ❌ CUDA runtime
- ❌ Database data (unless you want it)
```

---

## 🔧 HOW Is This Installing?

### The Build Process (Step by Step)

#### What's Happening Right Now:

```dockerfile
# This is what Docker is executing:

1. Start with NVIDIA CUDA base image
   FROM nvidia/cuda:12.6.0-runtime-ubuntu22.04
   ↓ Downloads 2.5GB CUDA environment

2. Update system packages
   RUN apt-get update && apt-get install -y \
       python3.11 \
       python3-pip \
       build-essential \
       git
   ↓ Installs system tools

3. Install Python AI packages ← YOU ARE HERE
   RUN pip install \
       torch==2.1.0+cu121 \        # 2GB+ PyTorch with GPU
       transformers \              # Hugging Face models
       fastapi \                   # Web framework
       sqlalchemy \                # Database
       pillow \                    # Image processing
       pytesseract \               # OCR
       opencv-python \             # Computer vision
       ... (50+ packages)
   ↓ Downloads and installs AI libraries

4. Copy your application code
   COPY backend/ /app/
   ↓ Adds your Python files

5. Configure GPU access
   ENV NVIDIA_VISIBLE_DEVICES=all
   ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
   ↓ Tells container to use GPU

6. Set startup command
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
   ↓ Defines how to run the app
```

#### The Installation Process:

```
Docker Build Process:
├─ Read Dockerfile.backend.gpu
├─ Execute each line (RUN command)
│  ├─ Download packages from internet
│  │  └─ PyPI (Python Package Index)
│  │     └─ Downloads .whl files
│  ├─ Install in container filesystem
│  └─ Compile native extensions (C/C++)
└─ Save as Docker image (snapshot)
```

---

## 🎯 WHAT Is Being Installed?

### Complete List of Major Components

#### 1. System Layer (~500MB)
```
- Ubuntu 22.04 base system
- CUDA 12.6 runtime libraries
- Python 3.11 interpreter
- GCC compiler
- Git version control
- System libraries (libssl, libffi, etc.)
```

#### 2. CUDA/GPU Layer (~2GB)
```
- CUDA Runtime 12.6
- cuDNN (Deep Neural Network library)
- cuBLAS (Linear algebra on GPU)
- NCCL (Multi-GPU communication)
- GPU device drivers interface
```

#### 3. Python AI/ML Packages (~1.5GB)
**Deep Learning:**
```python
torch==2.1.0+cu121         # PyTorch with CUDA 12.1 support
torchvision                # Computer vision models
transformers               # NLP models (BERT, GPT, etc.)
sentence-transformers      # Text embeddings
```

**Natural Language Processing:**
```python
spacy                      # NLP toolkit
nltk                       # Natural Language Toolkit
langdetect                 # Language detection
textblob                   # Text processing
```

**Computer Vision/OCR:**
```python
pytesseract               # OCR engine
opencv-python             # Image processing
pillow                    # Image manipulation
pdf2image                 # PDF to image conversion
```

**Web Framework:**
```python
fastapi                   # Modern web API framework
uvicorn                   # ASGI server
pydantic                  # Data validation
strawberry-graphql        # GraphQL support
```

**Database:**
```python
sqlalchemy               # ORM (Object-Relational Mapping)
alembic                  # Database migrations
psycopg2-binary         # PostgreSQL driver
asyncpg                 # Async PostgreSQL
```

**Data Processing:**
```python
pandas                   # Data manipulation
numpy                    # Numerical computing
openpyxl                # Excel files
python-docx             # Word documents
```

**Storage/Search:**
```python
minio                    # Object storage client
opensearch-py           # Search engine client
redis                   # Caching
```

**Monitoring/Observability:**
```python
arize-phoenix           # ML monitoring
prometheus-client       # Metrics
opentelemetry          # Tracing
```

#### 4. AI Models (Downloaded on first use, ~1-5GB)
```
These download when you first use them:
- BERT models for embeddings
- Classification models
- OCR models
- Language detection models
```

---

## 🎯 WHAT FOR? (Why Each Component)

### Purpose of Each Layer:

#### CUDA/GPU Stack
**What:** NVIDIA libraries for GPU computing  
**Why:** Makes AI processing 7x faster  
**Without it:** CPU-only, much slower  
**Used for:** Running PyTorch models on GPU

#### PyTorch
**What:** Deep learning framework  
**Why:** Powers all AI features  
**Used for:** 
- Document classification
- Text embeddings
- Semantic search
- Entity extraction

#### Transformers
**What:** Pre-trained NLP models  
**Why:** Understand document content  
**Used for:**
- Reading and understanding text
- Extracting meaning
- Classification
- Summarization

#### Tesseract/OCR
**What:** Optical Character Recognition  
**Why:** Extract text from images/scans  
**Used for:**
- Scanned documents
- Images with text
- PDFs without text layer

#### FastAPI
**What:** Web framework  
**Why:** Provides REST API  
**Used for:**
- Receiving requests from frontend
- Serving AI predictions
- Managing documents

#### SQLAlchemy
**What:** Database toolkit  
**Why:** Store and query data  
**Used for:**
- Saving document metadata
- User accounts
- Search history
- Audit logs

#### OpenSearch/MinIO
**What:** Search engine + Object storage  
**Why:** Fast search and file storage  
**Used for:**
- Full-text search
- Storing actual document files
- Quick retrieval

---

## 📊 Total Size Breakdown

```
Backend Container:
├─ Base OS + CUDA:        2.5 GB
├─ Python packages:       1.5 GB
├─ Your code:             50 MB
└─ Cache/temp:            500 MB
                         ─────────
   TOTAL:                 ~4.5 GB

Frontend Container:       ~500 MB
Database Container:       ~200 MB
Storage Container:        ~100 MB
Search Container:         ~600 MB
                         ─────────
TOTAL ALL CONTAINERS:     ~6 GB
```

**This is why it takes time - downloading 6GB+ of software!**

---

## 💡 Simple Analogy

Think of it like this:

**Building a Kitchen:**

1. **WHERE:** Not in your living room, but in a separate container (like a food truck)
2. **HOW:** Following a recipe (Dockerfile) step by step
3. **WHAT:** Installing:
   - Appliances (CUDA = industrial oven with GPU power)
   - Tools (Python = chef's knives)
   - Ingredients (AI models = pre-made sauces)
   - Cookbooks (Libraries = cooking techniques)

**WHAT FOR:**
- Appliances → Fast cooking (GPU acceleration)
- Tools → Prepare ingredients (process data)
- Ingredients → Make meals (AI predictions)
- Cookbooks → Follow recipes (run algorithms)

---

## 🔍 Current Status

**Right now, Docker is:**
```
Installing Python packages (step 3/6 in the analogy)
├─ Downloaded: CUDA ✅
├─ Installed: System tools ✅
├─ Installing: PyTorch + AI packages ⏳ (YOU ARE HERE)
│  ├─ torch: 2GB
│  ├─ transformers: 500MB
│  ├─ 50+ other packages
│  └─ Compiling native extensions
└─ Next: Copy your code, configure, done
```

**Progress:** ~60% complete
**Time remaining:** ~10 minutes

---

## ✅ Key Takeaways

1. **WHERE:** Inside Docker containers (isolated, not cluttering your Windows)
2. **HOW:** Following Dockerfile instructions, downloading from internet
3. **WHAT:** 6GB of AI/ML software + your application code
4. **WHAT FOR:** Build a GPU-accelerated document AI system

**Your Windows system stays clean!**  
Everything is containerized. Delete containers = all gone, no traces.

---

**Bottom line:** It's building a complete AI environment in an isolated container, using your GPU for speed. Takes time because it's downloading gigabytes of AI software. But once done, it'll be fast! 🚀
