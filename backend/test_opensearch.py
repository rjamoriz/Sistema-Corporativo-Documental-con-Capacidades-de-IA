#!/usr/bin/env python3
"""
Test opensearch imports
"""
try:
    import opensearchpy
    print("✅ opensearchpy module available")
    print(f"  Available: {dir(opensearchpy)[:5]}...")
except ImportError as e:
    print("❌ opensearchpy not available:", e)

try:
    from opensearch_py import OpenSearch
    print("✅ opensearch_py.OpenSearch available")
except ImportError as e:
    print("❌ opensearch_py.OpenSearch not available:", e)

try:
    from opensearchpy import OpenSearch
    print("✅ opensearchpy.OpenSearch available")
except ImportError as e:
    print("❌ opensearchpy.OpenSearch not available:", e)
