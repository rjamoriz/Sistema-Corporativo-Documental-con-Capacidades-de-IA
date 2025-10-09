#!/bin/bash
# FinancIA 2030 - Test Script
# Runs comprehensive test suite

set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR/.."

echo "🧪 Running FinancIA 2030 Test Suite"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r backend/requirements.txt
    pip install pytest pytest-asyncio pytest-cov httpx
else
    source venv/bin/activate
fi

# Check if services are running
echo "🔍 Checking if services are running..."
cd infrastructure/docker
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Services not running. Starting test environment..."
    docker-compose up -d postgres redis
    sleep 10
fi
cd ../..

# Create test environment file
if [ ! -f ".env.test" ]; then
    echo "📝 Creating test environment configuration..."
    cp .env.example .env.test
    # Override with test values
    sed -i 's/financia_db/financia_test_db/g' .env.test
    sed -i 's/LOG_LEVEL=INFO/LOG_LEVEL=DEBUG/g' .env.test
fi

export $(grep -v '^#' .env.test | xargs)

# Run tests
echo ""
echo "🧪 Running unit tests..."
pytest backend/tests/unit -v --cov=backend --cov-report=term-missing || true

echo ""
echo "🧪 Running integration tests..."
pytest backend/tests/integration -v --cov=backend --cov-append --cov-report=term-missing || true

echo ""
echo "🧪 Running API tests..."
pytest backend/tests/api -v --cov=backend --cov-append --cov-report=html || true

echo ""
echo "📊 Generating coverage report..."
echo "Coverage report available at: htmlcov/index.html"

# Run linting
echo ""
echo "🔍 Running code quality checks..."
if command -v black &> /dev/null; then
    echo "Running Black formatter check..."
    black --check backend/ || true
fi

if command -v flake8 &> /dev/null; then
    echo "Running Flake8 linter..."
    flake8 backend/ --max-line-length=120 --exclude=venv,__pycache__ || true
fi

if command -v mypy &> /dev/null; then
    echo "Running MyPy type checker..."
    mypy backend/ --ignore-missing-imports || true
fi

# Security checks
echo ""
echo "🔒 Running security checks..."
if command -v bandit &> /dev/null; then
    echo "Running Bandit security scanner..."
    bandit -r backend/ -ll || true
fi

if command -v safety &> /dev/null; then
    echo "Checking dependencies for vulnerabilities..."
    safety check --file=backend/requirements.txt || true
fi

echo ""
echo "✅ Test suite completed"
echo ""
echo "📈 Summary:"
echo "- Unit tests: Check output above"
echo "- Integration tests: Check output above"
echo "- API tests: Check output above"
echo "- Coverage report: htmlcov/index.html"
echo "- Code quality: Check linting output above"
