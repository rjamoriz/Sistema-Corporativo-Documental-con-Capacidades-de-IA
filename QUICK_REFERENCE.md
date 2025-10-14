# 🚀 WSL Deployment - Quick Reference Card

## 📍 YOU ARE HERE
Docker Desktop is restarting. Wait 60 seconds, then deploy.

---

## ⚡ Quick Commands

### Deploy
```powershell
.\deploy-gpu.ps1
# Choose option 1
```

### Fix Issues
```powershell
# Cache problems
.\fix-docker-cache.ps1

# Network problems
.\restart-docker.ps1
```

### Check Status
```powershell
# Container status
wsl bash -c "docker ps"

# View logs
wsl bash -c "docker logs financia_backend_gpu --tail 30"
```

---

## 🎯 Success Checklist

- [ ] Docker Desktop running (green icon in tray)
- [ ] Run `.\deploy-gpu.ps1`
- [ ] Choose option 1 (GPU-accelerated)
- [ ] Wait 25-35 minutes for build
- [ ] Check http://localhost:3000
- [ ] Login: admin.demo / Demo2025!

---

## 🐛 Common Errors

| Error | Fix |
|-------|-----|
| "parent snapshot" | `.\fix-docker-cache.ps1` |
| "TLS handshake timeout" | `.\restart-docker.ps1` |
| "port already allocated" | `wsl bash -c "docker-compose down"` |
| "cannot connect to daemon" | Start Docker Desktop |

---

## 📚 Full Documentation

- `WSL_DEPLOYMENT_TROUBLESHOOTING.md` - Complete troubleshooting
- `WSL_DEPLOYMENT_STATUS.md` - Current status and progress
- `GPU_QUICKSTART.md` - GPU deployment guide

---

## 🆘 Emergency Reset

```powershell
wsl bash -c "docker-compose down"
.\fix-docker-cache.ps1
.\restart-docker.ps1
# Wait 60 seconds
.\deploy-gpu.ps1
```

---

**Current Status:** Docker restarting - wait 60 seconds  
**Next Step:** Run `.\deploy-gpu.ps1`
