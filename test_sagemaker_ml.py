"""
Test script for SageMaker Predictive ML Service
"""

import requests
import json

BASE_URL = "http://localhost:8008"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_prediction_lightgbm():
    """Test prediction with LightGBM"""
    print("🤖 Testing LightGBM prediction with explanation...")
    
    payload = {
        "features": {
            "document_type": "credit_application",
            "amount": 25000.0,
            "duration": 24,
            "age": 35,
            "employment_duration": 60,
            "num_dependents": 2,
            "purpose": "car",
            "housing": "own",
            "job_type": "skilled",
            "document_id": "test_credit_001"
        },
        "explain": True,
        "model_type": "lightgbm"
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"Prediction: {result['prediction']}")
    print(f"Probability: {result['probability']:.2%}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Risk Score: {result['risk_score']:.1f}/100")
    
    if 'explanation' in result:
        print("\n📊 SHAP Explanation:")
        exp = result['explanation']
        for name, value, shap_val in zip(exp['feature_names'], exp['feature_values'], exp['shap_values']):
            impact = "↑" if shap_val > 0 else "↓"
            print(f"  {impact} {name}: {value} → SHAP: {shap_val:+.4f}")
        print(f"  Base Value: {exp['base_value']:.4f}")
    
    print(f"\nExecution Time: {result['execution_time']:.3f}s\n")

def test_prediction_xgboost():
    """Test prediction with XGBoost"""
    print("🌲 Testing XGBoost prediction...")
    
    payload = {
        "features": {
            "document_type": "loan_request",
            "amount": 50000.0,
            "duration": 36,
            "age": 45,
            "employment_duration": 120,
            "num_dependents": 1,
            "document_id": "test_loan_002"
        },
        "explain": True,
        "model_type": "xgboost"
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"Prediction: {result['prediction']}")
    print(f"Risk Score: {result['risk_score']:.1f}/100")
    print(f"Execution Time: {result['execution_time']:.3f}s\n")

def test_batch_prediction():
    """Test batch prediction"""
    print("📦 Testing batch prediction...")
    
    payload = {
        "features_list": [
            {
                "document_type": "credit",
                "amount": 10000.0,
                "duration": 12,
                "age": 25
            },
            {
                "document_type": "credit",
                "amount": 30000.0,
                "duration": 36,
                "age": 40
            },
            {
                "document_type": "loan",
                "amount": 75000.0,
                "duration": 60,
                "age": 50
            }
        ],
        "explain": False,
        "model_type": "lightgbm"
    }
    
    response = requests.post(f"{BASE_URL}/batch-predict", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"Total Processed: {result['total_processed']}")
    print(f"Execution Time: {result['execution_time']:.3f}s")
    
    print("\nResults:")
    for i, pred in enumerate(result['predictions'], 1):
        print(f"  {i}. Prediction: {pred['prediction']}, Risk: {pred['risk_score']:.1f}%")
    print()

def test_explain_only():
    """Test explanation only endpoint"""
    print("🔍 Testing explanation-only endpoint...")
    
    payload = {
        "features": {
            "document_type": "credit",
            "amount": 20000.0,
            "duration": 24,
            "age": 30,
            "employment_duration": 36
        },
        "explain": True,
        "model_type": "lightgbm"
    }
    
    response = requests.post(f"{BASE_URL}/explain", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"Prediction: {result['prediction']}")
    print(f"Risk Score: {result['risk_score']:.1f}/100")
    
    if 'explanation' in result:
        print("\nTop Feature Contributions:")
        exp = result['explanation']
        contributions = list(zip(exp['feature_names'], exp['shap_values']))
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        
        for name, shap_val in contributions[:3]:
            impact = "Increases" if shap_val > 0 else "Decreases"
            print(f"  • {name}: {impact} risk by {abs(shap_val):.4f}")
    print()

def test_models_info():
    """Test models information"""
    print("📊 Testing models information...")
    
    response = requests.get(f"{BASE_URL}/models/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_stats():
    """Test service statistics"""
    print("📈 Testing service statistics...")
    
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_high_risk_scenario():
    """Test high-risk scenario"""
    print("⚠️ Testing HIGH RISK scenario...")
    
    payload = {
        "features": {
            "document_type": "credit",
            "amount": 100000.0,  # High amount
            "duration": 12,       # Short duration
            "age": 22,            # Young age
            "employment_duration": 6,  # Short employment
            "num_dependents": 4   # Many dependents
        },
        "explain": True,
        "model_type": "lightgbm"
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    result = response.json()
    
    print(f"Risk Score: {result['risk_score']:.1f}/100")
    print(f"Prediction: {'APPROVED' if result['prediction'] == 0 else 'REJECTED'}")
    print()

def test_low_risk_scenario():
    """Test low-risk scenario"""
    print("✅ Testing LOW RISK scenario...")
    
    payload = {
        "features": {
            "document_type": "credit",
            "amount": 5000.0,     # Low amount
            "duration": 48,       # Long duration
            "age": 45,            # Mature age
            "employment_duration": 180,  # Long employment
            "num_dependents": 0   # No dependents
        },
        "explain": True,
        "model_type": "lightgbm"
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    result = response.json()
    
    print(f"Risk Score: {result['risk_score']:.1f}/100")
    print(f"Prediction: {'APPROVED' if result['prediction'] == 0 else 'REJECTED'}")
    print()

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 SAGEMAKER PREDICTIVE ML SERVICE - TEST SUITE")
    print("=" * 70 + "\n")
    
    try:
        test_health()
        test_models_info()
        test_prediction_lightgbm()
        test_prediction_xgboost()
        test_batch_prediction()
        test_explain_only()
        test_high_risk_scenario()
        test_low_risk_scenario()
        test_stats()
        
        print("=" * 70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
