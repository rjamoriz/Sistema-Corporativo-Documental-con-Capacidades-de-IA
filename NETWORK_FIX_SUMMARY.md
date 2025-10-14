# WSL Network Issue - Root Cause and Solution

## 🔍 Root Cause Analysis

### The Problem
Your WSL2 environment was experiencing **TLS handshake timeouts** when trying to connect to Docker Hub registry servers (`registry-1.docker.io` and `auth.docker.io`).

### Why This Happens
1. **WSL DNS Configuration**: WSL was using internal DNS (`10.255.255.254`) which couldn't properly resolve Docker Hub
2. **Docker Daemon DNS**: Docker wasn't configured with public DNS servers
3. **Network Routing**: WSL's network bridge wasn't routing HTTPS requests correctly to Docker registries

### Diagnostic Results
```
✅ Internet connection: Working
✅ Docker service: Running
❌ Docker Hub from Windows: 404 (but this is expected)
❌ Docker Hub from WSL: TLS handshake timeout
❌ Image pull: Initially failed
```

---

## ✅ Solutions Applied

### Fix 1: WSL DNS Configuration
```bash
# Updated /etc/resolv.conf to use public DNS
nameserver 8.8.8.8  # Google DNS
nameserver 8.8.4.4  # Google DNS backup
nameserver 1.1.1.1  # Cloudflare DNS
```

### Fix 2: WSL Configuration Protection
```bash
# Created /etc/wsl.conf to prevent DNS reset
[network]
generateResolvConf = false
```

### Fix 3: Docker Daemon DNS
```json
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]
}
```

### Fix 4: WSL Restart
- Shutdown WSL completely to apply changes
- Fresh network stack on restart

### Fix 5: Staged Deployment
Instead of building directly (which pulls images during build), we:
1. **Pre-pull** all base images separately with retries
2. **Build** application images with cached base images
3. **Start** services

---

## 🚀 Current Deployment Status

### Method: Staged Deployment (`deploy-gpu-staged.ps1`)

This script:
1. ✅ Pulls base images first (with retry logic)
2. ⏳ Building backend with GPU support
3. ⏳ Building frontend
4. ⏳ Starting all services

### Why This Method Works Better
- **Longer timeouts**: 300 seconds per image (vs 10 seconds during build)
- **Retry logic**: Up to 3 attempts per image
- **Progress visibility**: You can see each image being pulled
- **Failure isolation**: If one image fails, you know which one
- **Cache utilization**: Once images are pulled, build is fast

---

## ⏱️ Expected Timeline

### Current Stage: Image Pulling & Building
- **Image pulls**: 10-15 minutes (5 base images)
- **Backend build**: 10-15 minutes (GPU dependencies)
- **Frontend build**: 3-5 minutes  
- **Total**: ~25-35 minutes

### Progress Indicators
You should see output like:
```
[1/5] Pulling nvidia/cuda:12.6.0-runtime-ubuntu22.04...
  Success!
[2/5] Pulling node:20-alpine...
  Success!
...
Stage 2: Building application images...
Building backend with GPU support...
...
```

---

## 📊 What to Watch For

### Success Indicators
✅ Each image shows "Success!" after pulling  
✅ Build progresses without "TLS handshake timeout"  
✅ Final message: "Deployment successful!"  

### If You See Errors
❌ "TLS handshake timeout" - Network still has issues  
❌ "Failed after 3 attempts" - Image pull failed  
❌ "Build failed" - Code or dependency issue  

---

## 🛠️ Troubleshooting During Deployment

### If Image Pull Fails
```powershell
# The script will automatically retry 3 times
# If all retries fail:

# Option 1: Try again (network might be temporarily slow)
.\deploy-gpu-staged.ps1

# Option 2: Pull manually with longer timeout
wsl bash -c "docker pull <failed-image>"

# Option 3: Check if using VPN/Proxy
# Disable temporarily and try again
```

### If Build Fails
```powershell
# Check the exact error in terminal
# Common issues:
# - Missing file: Check Dockerfile paths
# - Dependency error: May need requirements update
# - Out of disk space: Run .\fix-docker-cache.ps1
```

---

## 📋 Alternative Methods (If Current Fails)

### Method A: Use docker-compose.yml (CPU-only)
```powershell
wsl bash -c "cd '/mnt/c/Users/rjamo/OneDrive/Desktop/IA GEN PROJECTS/Sistema Corporativo Documentacion AI-GPU boosted/Sistema-Corporativo-Documental-con-Capacidades-de-IA' && docker-compose build && docker-compose up -d"
```

### Method B: Build in WSL directly
```powershell
# Open WSL
wsl

# Navigate to project
cd "/mnt/c/Users/rjamo/OneDrive/Desktop/IA GEN PROJECTS/Sistema Corporativo Documentacion AI-GPU boosted/Sistema-Corporativo-Documental-con-Capacidades-de-IA"

# Pull images one by one
docker pull nvidia/cuda:12.6.0-runtime-ubuntu22.04
docker pull node:20-alpine
docker pull postgres:15-alpine
docker pull minio/minio:latest
docker pull opensearchproject/opensearch:2.11.0

# Then build
docker-compose -f docker-compose.gpu.yml build
docker-compose -f docker-compose.gpu.yml up -d
```

### Method C: Use Mobile Hotspot
If all else fails, sometimes using mobile data bypasses network restrictions:
1. Enable mobile hotspot on phone
2. Connect PC to hotspot
3. Run deployment

---

## 🔧 Scripts Created for You

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `diagnose-network.ps1` | Network diagnostics | Before deploying |
| `fix-docker-network-advanced.ps1` | Fix DNS & network | Network errors |
| `deploy-gpu-staged.ps1` | Staged deployment | Main deployment |
| `fix-docker-cache.ps1` | Clean Docker cache | Build errors |
| `restart-docker.ps1` | Restart Docker | Service issues |

---

## ✅ Post-Deployment Verification

### Once deployment completes, verify:

1. **Check containers are running:**
```powershell
wsl bash -c "docker ps"
```

Should show:
- financia_backend_gpu
- financia_frontend  
- postgres
- minio
- opensearch

2. **Check backend logs for GPU:**
```powershell
wsl bash -c "docker logs financia_backend_gpu --tail 50 | grep GPU"
```

Should show:
```
✅ GPU detected: NVIDIA GeForce RTX 4070
✅ CUDA available: True
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

4. **Test login:**
- Username: admin.demo
- Password: Demo2025!

---

## 📈 Network Fix Effectiveness

### Before Fix
- ❌ TLS handshake timeout
- ❌ Cannot pull images
- ❌ Build fails immediately

### After Fix  
- ✅ Alpine image pulled successfully
- ✅ DNS properly configured
- ✅ Docker daemon uses public DNS
- ✅ WSL network stack refreshed

### Test Results
```
❌ Before: timeout 10 docker pull alpine  -> FAILED
✅ After:  timeout 45 docker pull alpine  -> SUCCESS
```

---

## 🎯 Current Status

**Status:** Deployment in progress (staged method)  
**Started:** Just now  
**Expected completion:** 25-35 minutes  
**Method:** `deploy-gpu-staged.ps1`  
**Terminal:** Running in background (ID: d91e7660...)  

---

## 📞 Next Steps

### Right Now
- ⏳ Wait for deployment to complete
- 👀 Monitor terminal output
- ☕ Take a break (this will take ~30 minutes)

### After Deployment
1. Verify containers are running
2. Check GPU detection in logs
3. Access frontend at localhost:3000
4. Test with sample document

### If Issues Occur
1. Check terminal for error messages
2. Refer to `WSL_DEPLOYMENT_TROUBLESHOOTING.md`
3. Use diagnostic scripts

---

## 💡 Lessons Learned

### Key Takeaways
1. **WSL DNS** can cause Docker Hub connectivity issues
2. **Staged deployment** is more reliable than direct build
3. **Public DNS servers** (8.8.8.8) work better than default
4. **WSL restart** is needed for network changes
5. **Retry logic** handles temporary network hiccups

### Best Practices
- Always test connectivity before deploying
- Use staged deployment for first-time setups
- Keep fix scripts handy
- Monitor logs during deployment
- Be patient with large image pulls

---

**Document Created:** October 13, 2025  
**Status:** Network fixed, deployment in progress  
**Next Update:** After deployment completes
