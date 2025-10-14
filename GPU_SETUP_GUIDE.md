# 🎮 GPU Setup Guide for WSL2 + Docker

## Current Status
- ✅ NVIDIA GeForce RTX 4070 detected on Windows
- ✅ CUDA 12.8 Driver installed (573.09)
- ❌ GPU not accessible from WSL2 yet

## Setup Steps

### Step 1: Install NVIDIA Container Toolkit in WSL

Open your WSL terminal and run these commands:

```bash
# Configure the production repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update package list
sudo apt-get update

# Install NVIDIA Container Toolkit
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker
sudo systemctl restart docker || sudo service docker restart
```

### Step 2: Verify GPU Access in WSL

After installation, test GPU access:

```bash
# This should now work without errors
nvidia-smi
```

### Step 3: Test GPU in Docker

```bash
# Test GPU access in a container
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### Step 4: Re-enable GPU in docker-compose.yml

Once the above works, uncomment the GPU configuration in your docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      memory: 8G
    reservations:
      memory: 4G
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### Step 5: Rebuild and Start

```bash
# Rebuild backend with GPU support
docker-compose build backend

# Start all services
docker-compose up -d
```

## Benefits of GPU Acceleration

With your RTX 4070, you'll get significant speedups for:
- 🚀 **ML Model Inference** (3-10x faster)
- 📊 **Document Embeddings** (5-15x faster)
- 🤖 **LLM Processing** (2-8x faster)
- 🔍 **Vector Search** (up to 100x faster for large datasets)

## Troubleshooting

### If `nvidia-smi` still fails in WSL:
1. Update Windows to the latest version
2. Update WSL: `wsl --update`
3. Ensure you're using WSL2: `wsl -l -v` (should show version 2)
4. Reinstall NVIDIA drivers on Windows (download from nvidia.com)

### If Docker can't access GPU:
1. Check Docker daemon config: `sudo cat /etc/docker/daemon.json`
2. Should contain:
   ```json
   {
     "runtimes": {
       "nvidia": {
         "path": "nvidia-container-runtime",
         "runtimeArgs": []
       }
     }
   }
   ```

### Docker Desktop Users:
If using Docker Desktop instead of native Docker in WSL:
1. Open Docker Desktop Settings
2. Go to "Resources" → "WSL Integration"
3. Enable integration with your WSL distro
4. Ensure "Enable GPU" is checked in settings

## Current Workaround (CPU-only)

For now, the system is configured to run on CPU. This works fine but will be slower for:
- Initial model loading
- Large batch document processing
- Real-time embedding generation

Once GPU is enabled, performance will improve significantly!
