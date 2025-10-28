"""
Test script for Quantum ML Service
"""

import requests
import json

BASE_URL = "http://localhost:8007"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_classification():
    """Test quantum classification"""
    print("⚛️ Testing quantum classification...")
    
    payload = {
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        "document_id": "test_doc_001"
    }
    
    response = requests.post(f"{BASE_URL}/qml/classify", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_optimization():
    """Test quantum embedding optimization"""
    print("🔧 Testing quantum embedding optimization...")
    
    payload = {
        "embeddings": [
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.2, 0.3, 0.4, 0.5]
        ],
        "target_dimension": 4
    }
    
    response = requests.post(f"{BASE_URL}/qml/optimize-embeddings", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_anomaly_detection():
    """Test quantum anomaly detection"""
    print("🚨 Testing quantum anomaly detection...")
    
    payload = {
        "embeddings": [
            [0.1, 0.2, 0.3, 0.4],
            [0.15, 0.25, 0.35, 0.45],
            [0.9, 0.8, 0.7, 0.6],  # Anomaly
            [0.12, 0.22, 0.32, 0.42]
        ],
        "threshold": 0.5
    }
    
    response = requests.post(f"{BASE_URL}/qml/detect-anomalies", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_circuit_info():
    """Test circuit information"""
    print("📊 Testing circuit information...")
    
    response = requests.get(f"{BASE_URL}/qml/circuit-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_stats():
    """Test service statistics"""
    print("📈 Testing service statistics...")
    
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 QUANTUM ML SERVICE - TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        test_health()
        test_classification()
        test_optimization()
        test_anomaly_detection()
        test_circuit_info()
        test_stats()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
