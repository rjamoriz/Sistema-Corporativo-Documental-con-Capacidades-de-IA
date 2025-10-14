#!/usr/bin/env python3
"""
Test script to diagnose ML services loading issues
"""
import traceback
import sys

def test_service(service_name, import_statement):
    print(f"\n🔍 Testing {service_name}...")
    try:
        exec(import_statement)
        print(f"✅ {service_name} loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ {service_name} failed: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    services_to_test = [
        ("extract_service", "from services.extract_service import extract_service"),
        ("classification_service", "from services.classification_service import classification_service"),
        ("rag_service", "from services.rag_service import rag_service"),
        ("search_service", "from services.search_service import search_service"),
        ("risk_service", "from services.risk_service import risk_service"),
        ("compliance_service", "from services.compliance_service import compliance_service"),
    ]
    
    successful = 0
    total = len(services_to_test)
    
    for service_name, import_statement in services_to_test:
        if test_service(service_name, import_statement):
            successful += 1
    
    print(f"\n📊 Results: {successful}/{total} services loaded successfully")
    
    if successful == total:
        print("🎉 All services working! Ready to start full backend.")
    else:
        print("⚠️ Some services need fixes before full backend can start.")
