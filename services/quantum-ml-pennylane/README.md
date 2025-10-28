# ⚛️ Quantum ML Service - PennyLane

Servicio de Machine Learning Cuántico utilizando PennyLane para clasificación, optimización y detección de anomalías en documentos.

---

## 📊 Arquitectura del Componente

```mermaid
graph TB
    subgraph "Client Layer"
        CLIENT[Client Applications]
        API_GATEWAY[API Gateway]
    end
    
    subgraph "PennyLane QML Service - Port 8007"
        FASTAPI[FastAPI Server]
        
        subgraph "Quantum Models"
            VQC[Variational Quantum Classifier]
            QAUTO[Quantum Autoencoder]
            QANOM[Quantum Anomaly Detector]
        end
        
        subgraph "Quantum Backend"
            PENNYLANE[PennyLane Framework]
            QDEV[Quantum Device<br/>default.qubit]
            QCIRCUIT[Quantum Circuits<br/>4 qubits, 3 layers]
        end
        
        subgraph "Monitoring"
            PROM_METRICS[Prometheus Metrics]
            HEALTH[Health Check]
        end
    end
    
    subgraph "External Services"
        GPU_EMB[GPU Embedding Service<br/>Port 8001]
        ASTRA[Astra VectorDB<br/>Port 8006]
        PROMETHEUS[Prometheus<br/>Port 9090]
    end
    
    CLIENT --> API_GATEWAY
    API_GATEWAY --> FASTAPI
    
    FASTAPI --> VQC
    FASTAPI --> QAUTO
    FASTAPI --> QANOM
    
    VQC --> PENNYLANE
    QAUTO --> PENNYLANE
    QANOM --> PENNYLANE
    
    PENNYLANE --> QDEV
    QDEV --> QCIRCUIT
    
    FASTAPI --> PROM_METRICS
    FASTAPI --> HEALTH
    
    FASTAPI -.->|Get Embeddings| GPU_EMB
    FASTAPI -.->|Store Results| ASTRA
    PROM_METRICS -->|Scrape| PROMETHEUS
    
    style VQC fill:#e1f5ff
    style QAUTO fill:#e1f5ff
    style QANOM fill:#e1f5ff
    style PENNYLANE fill:#fff3e0
    style QDEV fill:#fff3e0
    style QCIRCUIT fill:#fff3e0
    style FASTAPI fill:#f3e5f5
```

### Flujo de Procesamiento

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant VQC as Quantum Classifier
    participant PL as PennyLane
    participant QD as Quantum Device
    participant P as Prometheus
    
    C->>API: POST /qml/classify
    Note over C,API: {embedding: [0.1, 0.2, ...]}
    
    API->>VQC: classify(embedding)
    VQC->>VQC: preprocess_input()
    Note over VQC: Normalize to [0, 2π]
    
    VQC->>PL: quantum_neural_network()
    PL->>QD: Execute circuit
    
    Note over QD: 1. AngleEmbedding<br/>2. StronglyEntanglingLayers<br/>3. Measure Pauli-Z
    
    QD-->>PL: quantum_output
    PL-->>VQC: expectation_values
    
    VQC->>VQC: softmax(quantum_output)
    VQC-->>API: classification_result
    
    API->>P: Update metrics
    Note over P: qml_requests_total++<br/>qml_latency_seconds
    
    API-->>C: JSON Response
    Note over C,API: {predicted_class: 2,<br/>confidence: 0.85,<br/>circuit_depth: 9}
```

### Circuito Cuántico Detallado

```mermaid
graph LR
    subgraph "Input Layer - Angle Encoding"
        I0["|0⟩"] --> RY0["RY(θ₁)"]
        I1["|0⟩"] --> RY1["RY(θ₂)"]
        I2["|0⟩"] --> RY2["RY(θ₃)"]
        I3["|0⟩"] --> RY3["RY(θ₄)"]
    end
    
    subgraph "Entangling Layer 1"
        RY0 --> CNOT01["CNOT"]
        RY1 --> CNOT01
        CNOT01 --> RY4["RY(φ₁)"]
        
        RY2 --> CNOT23["CNOT"]
        RY3 --> CNOT23
        CNOT23 --> RY5["RY(φ₂)"]
    end
    
    subgraph "Entangling Layer 2"
        RY4 --> CNOT12["CNOT"]
        RY5 --> CNOT12
        CNOT12 --> RY6["RY(ψ₁)"]
    end
    
    subgraph "Measurement"
        RY6 --> M0["⟨Z₀⟩"]
        RY6 --> M1["⟨Z₁⟩"]
        RY6 --> M2["⟨Z₂⟩"]
        RY6 --> M3["⟨Z₃⟩"]
    end
    
    M0 --> OUT[Output Vector]
    M1 --> OUT
    M2 --> OUT
    M3 --> OUT
    
    style I0 fill:#e3f2fd
    style I1 fill:#e3f2fd
    style I2 fill:#e3f2fd
    style I3 fill:#e3f2fd
    style CNOT01 fill:#fff9c4
    style CNOT23 fill:#fff9c4
    style CNOT12 fill:#fff9c4
    style M0 fill:#c8e6c9
    style M1 fill:#c8e6c9
    style M2 fill:#c8e6c9
    style M3 fill:#c8e6c9
    style OUT fill:#ffccbc
```

### Métricas y Monitoreo

```mermaid
graph TB
    subgraph "Quantum ML Service Metrics"
        QML[Quantum ML Service]
        
        QML --> M1[qml_requests_total<br/>Counter]
        QML --> M2[qml_latency_seconds<br/>Histogram]
        QML --> M3[quantum_advantage_ratio<br/>Gauge]
        QML --> M4[quantum_circuit_depth<br/>Gauge]
    end
    
    subgraph "Prometheus"
        PROM[Prometheus Server]
        SCRAPE[Scrape /metrics<br/>every 10s]
    end
    
    subgraph "Grafana Dashboards"
        D1[QML Performance]
        D2[Circuit Metrics]
        D3[Quantum Advantage]
    end
    
    M1 --> SCRAPE
    M2 --> SCRAPE
    M3 --> SCRAPE
    M4 --> SCRAPE
    
    SCRAPE --> PROM
    
    PROM --> D1
    PROM --> D2
    PROM --> D3
    
    style QML fill:#e1f5ff
    style PROM fill:#fff3e0
    style D1 fill:#f3e5f5
    style D2 fill:#f3e5f5
    style D3 fill:#f3e5f5
```

---

## 🎯 Características

### Modelos Implementados

1. **Variational Quantum Classifier (VQC)**
   - Clasificación de documentos usando redes neuronales cuánticas
   - StronglyEntanglingLayers para máxima expresividad
   - Angle encoding para datos clásicos

2. **Quantum Autoencoder**
   - Compresión de embeddings
   - Reducción de dimensionalidad cuántica
   - Optimización de representaciones

3. **Quantum Anomaly Detector**
   - Detección de anomalías usando métricas de distancia cuántica
   - Quantum k-Means clustering
   - Análisis de outliers

## 🚀 Endpoints

### Clasificación
```bash
POST /qml/classify
```

**Request:**
```json
{
  "embedding": [0.1, 0.2, 0.3, 0.4],
  "document_id": "doc_123",
  "metadata": {}
}
```

**Response:**
```json
{
  "predicted_class": 2,
  "confidence": 0.85,
  "quantum_output": [-0.5, 0.3, 0.8, -0.2],
  "probabilities": [0.05, 0.10, 0.85, 0.00],
  "circuit_depth": 9,
  "execution_time": 0.15
}
```

### Optimización de Embeddings
```bash
POST /qml/optimize-embeddings
```

**Request:**
```json
{
  "embeddings": [
    [0.1, 0.2, 0.3, 0.4],
    [0.5, 0.6, 0.7, 0.8]
  ],
  "target_dimension": 4
}
```

**Response:**
```json
{
  "optimized_embeddings": [[...], [...]],
  "compression_ratio": 2.5,
  "reconstruction_error": 0.05,
  "execution_time": 0.25
}
```

### Detección de Anomalías
```bash
POST /qml/detect-anomalies
```

**Request:**
```json
{
  "embeddings": [[...], [...], [...]],
  "threshold": 0.8
}
```

**Response:**
```json
{
  "anomalies": [2, 5],
  "scores": [0.3, 0.5, 0.9, 0.4, 0.6, 0.95],
  "threshold": 0.8,
  "execution_time": 0.30
}
```

### Información del Circuito
```bash
GET /qml/circuit-info
```

**Response:**
```json
{
  "n_qubits": 4,
  "n_layers": 3,
  "circuit_depth": 9,
  "total_gates": 36,
  "device": "default.qubit",
  "backend": "default.qubit"
}
```

## 🔧 Configuración

### Variables de Entorno

```bash
SERVICE_PORT=8007
N_QUBITS=4
N_LAYERS=3
LOG_LEVEL=INFO
```

### Docker

```bash
# Build
docker build -t quantum-ml-pennylane .

# Run
docker run -p 8007:8007 \
  -e N_QUBITS=4 \
  -e N_LAYERS=3 \
  quantum-ml-pennylane
```

### Docker Compose

```yaml
quantum-ml-pennylane:
  build: ./services/quantum-ml-pennylane
  ports:
    - "8007:8007"
  environment:
    - SERVICE_PORT=8007
    - N_QUBITS=4
    - N_LAYERS=3
```

## 📊 Arquitectura Cuántica

### Variational Quantum Circuit

```
|0⟩ ─── RY(θ₁) ─── ● ─── RY(φ₁) ─── ● ─── ⟨Z⟩
                   │                 │
|0⟩ ─── RY(θ₂) ─── X ─── RY(φ₂) ─── X ─── ⟨Z⟩
                   │                 │
|0⟩ ─── RY(θ₃) ─── ● ─── RY(φ₃) ─── ● ─── ⟨Z⟩
                   │                 │
|0⟩ ─── RY(θ₄) ─── X ─── RY(φ₄) ─── X ─── ⟨Z⟩
```

### Capas del Circuito

1. **Angle Embedding**: Codifica datos clásicos en estados cuánticos
2. **Strongly Entangling Layers**: Crea entrelazamiento entre qubits
3. **Measurement**: Mide expectation values de Pauli-Z

## 🧪 Testing

### Test Local

```python
import requests

# Clasificación
response = requests.post(
    "http://localhost:8007/qml/classify",
    json={
        "embedding": [0.1, 0.2, 0.3, 0.4]
    }
)
print(response.json())
```

### Benchmark

```bash
# Latencia
curl http://localhost:8007/qml/circuit-info

# Health
curl http://localhost:8007/health

# Métricas
curl http://localhost:8007/metrics
```

## 📈 Métricas Prometheus

- `qml_requests_total` - Total de requests por endpoint
- `qml_latency_seconds` - Latencia de requests
- `quantum_advantage_ratio` - Ventaja cuántica vs clásico
- `quantum_circuit_depth` - Profundidad del circuito

## 🔬 Ventaja Cuántica

### Casos de Uso Óptimos

1. **Alta Dimensionalidad**: Embeddings de 512+ dimensiones
2. **Datos Entrelazados**: Correlaciones complejas
3. **Pocos Datos**: Mejor generalización con datasets pequeños
4. **Optimización**: Espacios de búsqueda exponenciales

### Limitaciones

1. **Ruido Cuántico**: Simuladores perfectos, hardware real tiene errores
2. **Escalabilidad**: Limitado por número de qubits disponibles
3. **Latencia**: Más lento que modelos clásicos optimizados
4. **Costo**: Hardware cuántico real es costoso

## 🎓 Referencias

- [PennyLane Documentation](https://pennylane.ai/)
- [Quantum Machine Learning](https://pennylane.ai/qml/)
- [Variational Quantum Algorithms](https://arxiv.org/abs/2012.09265)
- [Quantum Autoencoders](https://arxiv.org/abs/1612.02806)

## 📝 Notas de Implementación

### Preprocesamiento

Los embeddings se normalizan a [0, 2π] para angle encoding:

```python
normalized = (x - x.min()) / (x.max() - x.min()) * 2 * π
```

### Entrenamiento

Actualmente usa pesos aleatorios. Para entrenar:

```python
# TODO: Implementar training loop
optimizer = qml.GradientDescentOptimizer(stepsize=0.01)
for epoch in range(100):
    weights = optimizer.step(cost_function, weights)
```

### Backends Disponibles

- `default.qubit` - Simulador CPU (actual)
- `lightning.qubit` - Simulador GPU (rápido)
- `qiskit.aer` - Simulador IBM
- `qiskit.ibmq` - Hardware IBM real (requiere token)

## 🚧 Roadmap

- [ ] Implementar training loop
- [ ] Añadir más backends (Lightning, Qiskit)
- [ ] Quantum Transfer Learning
- [ ] Hybrid Quantum-Classical layers
- [ ] Quantum Generative Models
- [ ] Integration con AutoML

## 📄 Licencia

MIT License - FinancIA 2030 Team
