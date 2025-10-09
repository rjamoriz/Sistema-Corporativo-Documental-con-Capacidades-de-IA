#!/bin/bash
# FinancIA 2030 - Setup Script
# Initializes the development environment

set -e

echo "🚀 FinancIA 2030 - Setup Script"
echo "================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration (especially OPENAI_API_KEY)"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/logs
mkdir -p data/{contracts,identity_docs,invoices,provider_contracts,insurance,audio,video,misc,golden_set}
mkdir -p infrastructure/docker

echo "✅ Directories created"

# Pull Docker images
echo "🐳 Pulling Docker images (this may take a while)..."
cd infrastructure/docker
docker-compose pull

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run './scripts/start.sh' to start all services"
echo "3. Access the API at http://localhost:8000/docs"
