#!/bin/bash
# Quick GPU test script

echo "🧪 Quick GPU Test for FinancIA 2030"
echo "===================================="

# Test 1: Docker GPU access
echo ""
echo "Test 1: Docker GPU Access"
echo "-------------------------"
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi

if [ $? -eq 0 ]; then
    echo "✅ Docker can access GPU"
else
    echo "❌ Docker cannot access GPU"
    exit 1
fi

# Test 2: Check if backend container is running
echo ""
echo "Test 2: Backend Container Status"
echo "--------------------------------"
if docker ps | grep -q financia_backend; then
    CONTAINER=$(docker ps --filter "name=financia_backend" --format "{{.Names}}")
    echo "✅ Backend container running: $CONTAINER"
    
    # Test 3: GPU verification inside container
    echo ""
    echo "Test 3: GPU Status Inside Container"
    echo "-----------------------------------"
    docker exec $CONTAINER python check_gpu.py
    
    if [ $? -eq 0 ]; then
        echo "✅ GPU working inside container"
    else
        echo "⚠️  GPU not detected inside container"
    fi
else
    echo "⚠️  Backend container not running"
    echo "Run: docker-compose up -d"
fi

echo ""
echo "===================================="
echo "✅ Test complete!"
