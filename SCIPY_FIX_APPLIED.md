# Fix Applied: scipy/numpy Compatibility Issue

## 🔧 Problem Identified
The backend container was crashing with a scipy/numpy incompatibility error:
```
ValueError: All ufuncs must have type `numpy.ufunc`. Received ...
```

## ✅ Solution Applied

### Changes to `Dockerfile.backend.gpu`:
```dockerfile
# Instalar numpy y scipy primero con versiones compatibles
RUN pip install --no-cache-dir numpy==1.26.4 scipy==1.11.4

# Instalar PyTorch con soporte CUDA (optimizado para CUDA 12.x)
RUN pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121

# Remover paquetes problemáticos instalados por distutils
RUN pip install --ignore-installed blinker || true

# Instalar el resto de dependencias Python (excluyendo numpy y scipy que ya están instalados)
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt
```

## 📋 What We Did
1. **Pinned numpy to 1.26.4** - This is compatible with scipy 1.11.x
2. **Pinned scipy to 1.11.4** - Latest stable release compatible with numpy 1.26.x
3. **Installed them FIRST** - Before PyTorch and other dependencies to ensure compatibility
4. **Installed PyTorch with CUDA 12.1** - For GPU acceleration
5. **Installed remaining requirements** - Using `--ignore-installed` to handle conflicts

## 🎯 Expected Outcome
- Backend container will start successfully
- GPU will be detected (RTX 4070 8GB)
- All services will run without restarts
- System will be accessible at:
  - Frontend: http://localhost:3000
  - Backend API: http://localhost:8000/docs

## 🚀 Next Steps
1. Wait for rebuild to complete (~3-5 minutes)
2. Start the backend container
3. Verify GPU detection
4. Test system functionality

## ⚠️ Note on Package Versions
These versions were chosen for compatibility with:
- Python 3.11
- PyTorch 2.1.0 with CUDA 12.1
- scikit-learn (requires scipy)
- sentence-transformers (requires scipy)

## 📝 Rebuild Command Used
```bash
docker stop financia_backend_gpu && docker rm financia_backend_gpu
docker-compose build backend
docker-compose up -d backend
```

---
**Status**: ⏳ Rebuilding container...
**Time**: ~3-5 minutes for complete rebuild
**GPU**: NVIDIA GeForce RTX 4070 Laptop GPU (8GB VRAM)
