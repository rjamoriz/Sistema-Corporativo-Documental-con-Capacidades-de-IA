#!/usr/bin/env python3
"""
Script de verificación de GPU para FinancIA 2030
Verifica la disponibilidad y configuración de GPU en el sistema
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_gpu_availability():
    """Verifica si GPU está disponible y configurada correctamente"""
    
    print("=" * 80)
    print("🔍 GPU VERIFICATION FOR FINANCIA 2030")
    print("=" * 80)
    
    # 1. Verificar PyTorch
    try:
        import torch
        print(f"\n✅ PyTorch version: {torch.__version__}")
        
        cuda_available = torch.cuda.is_available()
        print(f"✅ CUDA available: {cuda_available}")
        
        if cuda_available:
            print(f"✅ CUDA version: {torch.version.cuda}")
            print(f"✅ cuDNN version: {torch.backends.cudnn.version()}")
            print(f"✅ Number of GPUs: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                print(f"\n📊 GPU {i}: {torch.cuda.get_device_name(i)}")
                print(f"   - Total memory: {props.total_memory / 1024**3:.2f} GB")
                print(f"   - Compute capability: {props.major}.{props.minor}")
                print(f"   - Multi-processor count: {props.multi_processor_count}")
            
            # Test básico de GPU
            print("\n🧪 Running GPU test...")
            x = torch.rand(1000, 1000).cuda()
            y = torch.rand(1000, 1000).cuda()
            z = torch.matmul(x, y)
            print(f"✅ GPU computation successful! Result shape: {z.shape}")
            
            # Limpiar memoria
            del x, y, z
            torch.cuda.empty_cache()
            
        else:
            print("⚠️  WARNING: GPU not detected! Running in CPU mode.")
            print("   This will significantly impact performance.")
            
    except ImportError:
        print("❌ ERROR: PyTorch not installed!")
        return False
    except Exception as e:
        print(f"❌ ERROR checking PyTorch: {e}")
        return False
    
    # 2. Verificar transformers
    try:
        import transformers
        print(f"\n✅ Transformers version: {transformers.__version__}")
    except ImportError:
        print("⚠️  WARNING: Transformers not installed")
    
    # 3. Verificar sentence-transformers
    try:
        import sentence_transformers
        print(f"✅ Sentence-Transformers version: {sentence_transformers.__version__}")
    except ImportError:
        print("⚠️  WARNING: Sentence-Transformers not installed")
    
    # 4. Verificar spaCy
    try:
        import spacy
        print(f"✅ spaCy version: {spacy.__version__}")
    except ImportError:
        print("⚠️  WARNING: spaCy not installed")
    
    # 5. Resumen de memoria GPU
    if cuda_available:
        print("\n" + "=" * 80)
        print("📊 GPU MEMORY SUMMARY")
        print("=" * 80)
        for i in range(torch.cuda.device_count()):
            allocated = torch.cuda.memory_allocated(i) / 1024**3
            reserved = torch.cuda.memory_reserved(i) / 1024**3
            total = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"GPU {i}:")
            print(f"  - Allocated: {allocated:.2f} GB")
            print(f"  - Reserved: {reserved:.2f} GB")
            print(f"  - Total: {total:.2f} GB")
            print(f"  - Free: {total - reserved:.2f} GB")
    
    print("\n" + "=" * 80)
    print("✅ GPU VERIFICATION COMPLETE")
    print("=" * 80 + "\n")
    
    return cuda_available

if __name__ == "__main__":
    gpu_available = check_gpu_availability()
    sys.exit(0 if gpu_available else 1)
