#!/usr/bin/env python3
"""
GPU Access Test Script
Simple test to verify if GPU is available and accessible from Docker container
"""

import sys
import platform

def check_gpu_support():
    """Check if GPU/CUDA support is available"""
    print("=== System Information ===")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print()
    
    # Check PyTorch CUDA availability
    print("=== PyTorch GPU Check ===")
    try:
        import torch
        print(f"PyTorch Version: {torch.__version__}")
        print(f"CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA Version: {torch.version.cuda}")
            print(f"GPU Device Count: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                memory_gb = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"GPU {i}: {gpu_name} ({memory_gb:.1f} GB)")
                
            # Test tensor operations
            print("\n=== GPU Tensor Test ===")
            device = torch.device("cuda:0")
            x = torch.randn(10, 10).to(device)
            y = torch.randn(10, 10).to(device)
            z = torch.matmul(x, y)
            print(f"Matrix multiplication on GPU successful: {z.device}")
        else:
            print("No CUDA-capable GPU detected")
            
    except ImportError:
        print("PyTorch not installed")
    except Exception as e:
        print(f"Error checking PyTorch GPU: {e}")
    
    # Check system GPU info
    print("\n=== System GPU Information ===")
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("nvidia-smi output:")
            print(result.stdout)
        else:
            print("nvidia-smi not available or failed")
    except FileNotFoundError:
        print("nvidia-smi command not found")
    except Exception as e:
        print(f"Error running nvidia-smi: {e}")

if __name__ == "__main__":
    check_gpu_support()
