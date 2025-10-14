# WSL Deployment Troubleshooting Guide

## Table of Contents
1. [Common Issues](#common-issues)
2. [Docker-Specific Issues](#docker-specific-issues)
3. [Network Issues](#network-issues)
4. [Performance Issues](#performance-issues)
5. [Port Conflicts](#port-conflicts)
6. [Memory & Resource Issues](#memory--resource-issues)
7. [File System Issues](#file-system-issues)
8. [Diagnostic Commands](#diagnostic-commands)
9. [Recovery Procedures](#recovery-procedures)

---

## Common Issues

### Issue 1: Docker Daemon Not Running
**Symptoms:**
- Error: "Cannot connect to the Docker daemon"
- Docker commands fail

**Solutions:**
```bash
# Check Docker service status
sudo service docker status

# Start Docker service
sudo service docker start

# Enable Docker to start on boot
sudo systemctl enable docker

# Restart Docker
sudo service docker restart
```

### Issue 2: Permission Denied Errors
**Symptoms:**
- "Permission denied" when running Docker commands
- Cannot access files or directories

**Solutions:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes (logout/login or run)
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

### Issue 3: WSL Integration Issues
**Symptoms:**
- Docker Desktop not accessible from WSL
- "docker: command not found"

**Solutions:**
1. Open Docker Desktop on Windows
2. Go to Settings → Resources → WSL Integration
3. Enable integration for your WSL distribution
4. Restart WSL:
```powershell
# In PowerShell (Windows)
wsl --shutdown
wsl
```

---

## Docker-Specific Issues

### Issue 4: Docker Cache Corruption
**Symptoms:**
- "parent snapshot does not exist: not found"
- "failed to prepare extraction snapshot"
- Build fails during image export

**Quick Fix (PowerShell):**
```powershell
# Run the automated fix script
.\fix-docker-cache.ps1

# Then redeploy
.\deploy-gpu.ps1
```

**Manual Fix (WSL/Linux):**
```bash
# Stop all containers
docker-compose down

# Clean builder cache
docker builder prune -a -f

# Remove dangling images
docker image prune -f

# Clean system
docker system prune -f

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Issue 5: Build Failures
**Symptoms:**
- "docker build" command fails
- Image build errors

**Diagnostic Steps:**
```bash
# Check Docker version
docker --version
docker-compose --version

# Verify Docker is running
docker ps

# Check Docker logs
docker logs <container_name>

# Inspect build cache
docker system df
```

**Solutions:**
```bash
# Clear Docker cache
docker builder prune -a

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Complete cleanup (USE WITH CAUTION)
docker system prune -a --volumes

# Rebuild without cache
docker-compose build --no-cache
```

### Issue 6: Container Startup Failures
**Symptoms:**
- Containers exit immediately
- "Exited (1)" or other error codes

**Diagnostic Steps:**
```bash
# View container logs
docker-compose logs backend
docker-compose logs frontend

# Check container status
docker-compose ps

# Inspect container
docker inspect <container_name>

# View last 100 lines of logs
docker-compose logs --tail=100 backend
```

**Solutions:**
```bash
# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend

# Start in foreground to see errors
docker-compose up backend
```

---

## Network Issues

### Issue 6: Docker Hub TLS Handshake Timeout
**Symptoms:**
- "TLS handshake timeout" when pulling images
- "failed to resolve source metadata for docker.io"
- Cannot connect to Docker Hub registry

**Quick Fix (PowerShell):**
```powershell
# Run the automated network fix
.\fix-docker-network.ps1

# Wait 10 seconds, then redeploy
.\deploy-gpu.ps1
```

**Manual Fix (WSL):**
```bash
# Configure Docker DNS
sudo mkdir -p /etc/docker
echo '{"dns": ["8.8.8.8", "8.8.4.4"]}' | sudo tee /etc/docker/daemon.json

# Restart Docker
sudo service docker restart

# Wait 10 seconds
sleep 10

# Test connectivity
curl -I https://registry-1.docker.io
```

**Alternative Solutions:**
1. **Restart Docker Desktop** (Windows):
   - Right-click Docker Desktop icon
   - Select "Restart"
   - Wait for full initialization

2. **Check Windows Firewall**:
   - Allow Docker Desktop through firewall
   - Disable VPN if connected

3. **WSL DNS Fix**:
   ```bash
   # Edit WSL DNS settings
   sudo nano /etc/resolv.conf
   
   # Add these lines:
   nameserver 8.8.8.8
   nameserver 8.8.4.4
   
   # Save and restart Docker
   sudo service docker restart
   ```

4. **Use Local Cache** (if images were previously pulled):
   ```bash
   # List cached images
   docker images
   
   # Build without pulling new images
   docker-compose build --no-cache
   ```

### Issue 7: Cannot Access Services
**Symptoms:**
- Services not accessible via localhost
- Connection refused errors

**Diagnostic Steps:**
```bash
# Check if ports are listening
netstat -tuln | grep LISTEN

# Check WSL network
ip addr show

# Test connectivity
curl http://localhost:8000
curl http://localhost:3000
```

**Solutions:**
```bash
# In WSL, find WSL IP
hostname -I

# Access via WSL IP instead of localhost
# http://<WSL_IP>:3000

# Port forwarding (if needed)
# Add to ~/.bashrc or run manually:
alias port-forward='netsh.exe interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=$(hostname -I | awk "{print \$1}")'
```

**Windows Firewall:**
```powershell
# In PowerShell (Windows) - Allow ports
New-NetFirewallRule -DisplayName "WSL Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "WSL Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Issue 8: Docker Network Conflicts
**Symptoms:**
- "network already exists" errors
- Container cannot communicate

**Solutions:**
```bash
# List networks
docker network ls

# Remove specific network
docker network rm <network_name>

# Remove unused networks
docker network prune

# Recreate network
docker-compose down
docker network create sistema_corporativo_network
docker-compose up -d
```

---

## Performance Issues

### Issue 9: Slow Build Times
**Symptoms:**
- Docker builds take very long
- File operations are slow

**Solutions:**
```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Move project to WSL filesystem
# Instead of /mnt/c/..., use ~/projects/...
cd ~
mkdir -p projects
cp -r /mnt/c/Users/.../proyecto ~/projects/

# Update Docker Desktop settings:
# - Increase CPUs (Settings → Resources)
# - Increase Memory (Settings → Resources)
# - Enable WSL 2 backend
```

### Issue 10: High Memory Usage
**Symptoms:**
- System becomes slow
- Out of memory errors

**Diagnostic Steps:**
```bash
# Check container resource usage
docker stats

# Check system memory
free -h

# Check WSL memory
cat /proc/meminfo
```

**Solutions:**
```bash
# Limit container memory in docker-compose.yml
# Add under each service:
#   mem_limit: 2g
#   memswap_limit: 2g

# Configure WSL memory limit
# Create/edit: C:\Users\<username>\.wslconfig
```

**Example .wslconfig:**
```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
```

Then restart WSL:
```powershell
wsl --shutdown
```

---

## Port Conflicts

### Issue 11: Port Already in Use
**Symptoms:**
- "port is already allocated" error
- "address already in use"

**Diagnostic Steps:**
```bash
# Find what's using the port (in WSL)
sudo lsof -i :8000
sudo lsof -i :3000

# Or using netstat
sudo netstat -tulpn | grep :8000
```

**Solutions:**
```bash
# Stop conflicting service
sudo kill -9 <PID>

# Or stop Docker containers
docker-compose down

# Change ports in docker-compose.yml
# Edit ports section:
#   - "8001:8000"  # Use different host port
```

---

## Memory & Resource Issues

### Issue 12: Out of Disk Space
**Symptoms:**
- "no space left on device"
- Build failures due to disk space

**Diagnostic Steps:**
```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Check specific directory
du -sh ~/projects/*
```

**Solutions:**
```bash
# Clean Docker resources
docker system prune -a --volumes

# Remove old images
docker image prune -a

# Remove build cache
docker builder prune -a

# Clean package managers
sudo apt-get clean
sudo apt-get autoclean
```

### Issue 13: Python Package Installation Fails
**Symptoms:**
- "Cannot uninstall blinker"
- "distutils installed project"
- "exit code: 1" during pip install

**Cause:**
Some Python packages are pre-installed by the system using distutils (old installation method) and pip cannot upgrade them properly.

**Solution (Already Fixed):**
The Dockerfile now uses `--ignore-installed` flag:

```dockerfile
# Fix in Dockerfile.backend.gpu
RUN pip install --ignore-installed blinker || true
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt
```

**If you see this error:**
The deployment will automatically retry with the fixed Dockerfile.

**Manual fix if needed:**
```bash
# Edit Dockerfile.backend.gpu and add --ignore-installed flag
# Then rebuild:
wsl bash -c "docker-compose -f docker-compose.gpu.yml build --no-cache backend"
```

---

## File System Issues

### Issue 14: Line Ending Issues
**Symptoms:**
- Scripts fail with "^M" errors
- "command not found" for existing commands

**Solutions:**
```bash
# Convert line endings
dos2unix filename.sh

# If dos2unix not installed
sudo apt-get install dos2unix

# Or use sed
sed -i 's/\r$//' filename.sh

# Fix all shell scripts
find . -name "*.sh" -exec dos2unix {} \;
```

### Issue 15: File Permission Issues
**Symptoms:**
- Cannot execute scripts
- Permission denied on files

**Solutions:**
```bash
# Make script executable
chmod +x script.sh

# Fix all shell scripts
find . -name "*.sh" -exec chmod +x {} \;

# Reset permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
find . -name "*.sh" -exec chmod 755 {} \;
```

---

## Diagnostic Commands

### Quick Health Check
```bash
# Run all diagnostic commands at once
echo "=== Docker Status ==="
docker --version
docker-compose --version
docker ps

echo -e "\n=== System Resources ==="
free -h
df -h

echo -e "\n=== Network Status ==="
ip addr show
netstat -tuln | grep LISTEN

echo -e "\n=== Running Services ==="
docker-compose ps

echo -e "\n=== Recent Logs ==="
docker-compose logs --tail=20
```

### Container Debugging
```bash
# Enter running container
docker-compose exec backend bash
docker-compose exec frontend sh

# View environment variables
docker-compose exec backend env

# Check container processes
docker-compose exec backend ps aux

# Test database connection
docker-compose exec backend python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://user:pass@db:5432/dbname'); print(engine.connect())"
```

### Network Debugging
```bash
# Test connectivity between containers
docker-compose exec backend ping frontend
docker-compose exec backend curl http://frontend:3000

# Test external connectivity
docker-compose exec backend curl https://google.com

# Check DNS resolution
docker-compose exec backend nslookup google.com
```

---

## Recovery Procedures

### Complete Reset
```bash
# Stop all containers
docker-compose down

# Remove all containers, networks, volumes
docker-compose down -v

# Clean everything
docker system prune -a --volumes

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Backup Current State
```bash
# Export running containers
docker export <container_name> > backup.tar

# Save Docker images
docker save -o backup-images.tar image1 image2

# Backup volumes
docker run --rm -v <volume_name>:/data -v $(pwd):/backup alpine tar czf /backup/volume-backup.tar.gz /data
```

### Restore State
```bash
# Import container
docker import backup.tar

# Load images
docker load -i backup-images.tar

# Restore volume
docker run --rm -v <volume_name>:/data -v $(pwd):/backup alpine tar xzf /backup/volume-backup.tar.gz -C /
```

---

## Advanced Troubleshooting

### Enable Debug Logging
```bash
# Edit docker-compose.yml
# Add to backend service:
#   environment:
#     - LOG_LEVEL=DEBUG
#     - PYTHONUNBUFFERED=1

# Restart with verbose output
docker-compose up --verbose
```

### Monitor in Real-Time
```bash
# Follow logs
docker-compose logs -f

# Monitor specific service
docker-compose logs -f backend

# Watch resource usage
watch -n 1 'docker stats --no-stream'

# Watch processes
watch -n 1 'docker-compose ps'
```

### Database Issues
```bash
# Access PostgreSQL (if using)
docker-compose exec db psql -U username -d dbname

# Check database connection
docker-compose exec backend python -c "from backend.config.database import engine; print(engine.connect())"

# Run migrations
docker-compose exec backend alembic upgrade head

# Reset database (CAUTION: DELETES DATA)
docker-compose down -v
docker-compose up -d db
# Wait for db to start
sleep 10
docker-compose exec backend alembic upgrade head
```

---

## Preventive Measures

### Regular Maintenance
```bash
# Weekly cleanup
docker system prune -f

# Monthly full cleanup
docker system prune -a --volumes

# Update images
docker-compose pull
docker-compose up -d
```

### Monitoring Setup
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    clear
    echo "=== System Status at $(date) ==="
    echo
    docker-compose ps
    echo
    docker stats --no-stream
    sleep 5
done
EOF

chmod +x monitor.sh
./monitor.sh
```

---

## Getting Help

### Collect Debug Information
```bash
# Generate debug report
cat > debug-report.txt << EOF
=== System Info ===
$(uname -a)
$(docker --version)
$(docker-compose --version)

=== Docker Status ===
$(docker ps -a)

=== Logs ===
$(docker-compose logs --tail=100)

=== Resources ===
$(docker stats --no-stream)
$(free -h)
$(df -h)

=== Network ===
$(ip addr show)
$(docker network ls)
EOF

cat debug-report.txt
```

### Useful Resources
- Docker Documentation: https://docs.docker.com/
- WSL Documentation: https://docs.microsoft.com/en-us/windows/wsl/
- Docker Compose: https://docs.docker.com/compose/

---

## Quick Reference

### Essential Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Rebuild service
docker-compose up -d --build backend

# Check status
docker-compose ps

# Clean up
docker system prune -f
```

### Emergency Stop
```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Nuclear option (removes everything)
docker system prune -a --volumes -f
```

---

**Last Updated:** October 13, 2025
**Version:** 1.0
