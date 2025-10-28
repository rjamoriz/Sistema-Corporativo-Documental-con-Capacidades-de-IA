# 📚 Guía de Entrenamiento - Credit Risk ML Model

Esta guía explica cómo entrenar tu propio modelo de riesgo crediticio con tus datos históricos.

## 📋 Datos Necesarios

### Formato del CSV

Tu archivo CSV debe contener las siguientes columnas:

#### ✅ Columnas Requeridas (Estructuradas)

| Columna | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `age` | int | Edad del cliente | 35 |
| `income` | float | Ingresos anuales | 45000.0 |
| `employment_years` | int | Años de empleo | 8 |
| `credit_history_months` | int | Meses de historial crediticio | 48 |
| `num_previous_loans` | int | Número de préstamos previos | 3 |
| `num_defaults` | int | Número de impagos históricos | 0 |
| `loan_amount` | float | Monto del préstamo | 25000.0 |
| `loan_duration_months` | int | Duración del préstamo en meses | 60 |
| `customer_tenure_months` | int | Antigüedad como cliente | 36 |
| `num_products` | int | Productos contratados | 2 |
| `avg_balance` | float | Saldo promedio | 5000.0 |
| **`default`** | **int** | **Target: 0=no impago, 1=impago** | **0** |

#### 🔶 Columnas Opcionales (No Estructuradas)

| Columna | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `external_credit_score` | int | Score crediticio externo (300-850) | 720 |
| `doc_sentiment_score` | float | Sentiment de documentos (-1 a 1) | 0.65 |
| `risk_clauses_count` | int | Cláusulas de riesgo en contratos | 1 |
| `inconsistencies_detected` | int | Inconsistencias en documentos | 0 |
| `payment_delay_mentions` | int | Menciones de retrasos | 0 |
| `legal_issues_mentions` | int | Problemas legales mencionados | 0 |
| `restructuring_mentions` | int | Reestructuraciones mencionadas | 0 |
| `document_completeness` | float | Completitud documental (0-1) | 0.95 |
| `document_quality_score` | float | Calidad de documentos (0-1) | 0.90 |

### Ejemplo de CSV

```csv
age,income,employment_years,credit_history_months,num_previous_loans,num_defaults,external_credit_score,loan_amount,loan_duration_months,customer_tenure_months,num_products,avg_balance,doc_sentiment_score,risk_clauses_count,inconsistencies_detected,payment_delay_mentions,legal_issues_mentions,restructuring_mentions,document_completeness,document_quality_score,default
35,45000,8,48,3,0,720,25000,60,36,2,5000,0.65,1,0,0,0,0,0.95,0.90,0
42,65000,15,84,5,0,780,30000,48,60,3,12000,0.80,0,0,0,0,0,1.00,0.95,0
28,30000,3,24,1,1,620,15000,36,12,1,2000,-0.20,3,2,1,0,0,0.70,0.60,1
50,80000,20,120,8,0,800,40000,60,96,4,20000,0.75,0,0,0,0,0,1.00,1.00,0
25,25000,2,12,0,2,580,20000,48,6,1,500,-0.40,5,3,2,1,1,0.50,0.50,1
```

## 🚀 Cómo Entrenar el Modelo

### Opción 1: Usar el Script de Entrenamiento

```bash
# 1. Navegar al directorio del servicio
cd services/sklearn-credit-risk

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Entrenar con tus datos
python training.py --csv your_data.csv --tuning

# O usar datos de ejemplo
python training.py --generate-sample
```

### Opción 2: Usar Python Directamente

```python
from training import ModelTrainer

# Crear trainer
trainer = ModelTrainer(model_dir="./models")

# Entrenar con tus datos
results = trainer.train_pipeline(
    csv_path="your_credit_data.csv",
    test_size=0.2,                    # 20% para validación
    hyperparameter_tuning=True,       # Optimizar hiperparámetros
    contamination=0.05                # 5% de fraude esperado
)

# Ver resultados
print(f"AUC-ROC: {results['metrics']['auc_roc']:.4f}")
print(f"Version: {results['version']}")
```

### Opción 3: Generar Datos de Ejemplo

```python
from training import create_sample_csv, ModelTrainer

# 1. Generar CSV de ejemplo
csv_path = create_sample_csv(
    output_path="sample_data.csv",
    n_samples=5000
)

# 2. Entrenar
trainer = ModelTrainer()
results = trainer.train_pipeline(csv_path)
```

## 📊 Métricas de Evaluación

El entrenamiento proporciona las siguientes métricas:

| Métrica | Descripción | Objetivo |
|---|---|---|
| **AUC-ROC** | Área bajo la curva ROC | >0.80 |
| **AUC-PR** | Área bajo Precision-Recall | >0.70 |
| **Brier Score** | Calibración de probabilidades | <0.15 |
| **Log Loss** | Pérdida logarítmica | <0.50 |
| **Precision** | Precisión en clase positiva | >0.75 |
| **Recall** | Cobertura de defaults | >0.70 |
| **F1-Score** | Balance precision/recall | >0.72 |

### Ejemplo de Output

```
================================================================================
🚀 Starting training pipeline
================================================================================
📂 Loading data from credit_data.csv
✅ Loaded 5000 rows, 21 columns
✅ Data validation passed
   - Default rate: 15.20%
   - Samples: 5000 (Default: 760, No Default: 4240)
🔧 Engineering features...
✅ Features engineered: 43 total columns
📊 Preparing features...
✅ Features prepared: (5000, 22)
   - Features: 22
   - Samples: 5000
📊 Data split:
   - Train: 4000 samples (15.18% default)
   - Val: 1000 samples (15.30% default)
🎯 Training credit risk model...
📐 Calibrating probabilities...
✅ Credit risk model trained
   - AUC-ROC: 0.8542
   - AUC-PR: 0.7234
   - Brier Score: 0.1123
🔍 Training fraud detector...
✅ Fraud detector trained (contamination=0.05)
💾 Saving models to ./models
✅ Models saved:
   - Credit Risk: ./models/credit_risk_v20241028_184500.pkl
   - Fraud Detector: ./models/fraud_detector_v20241028_184500.pkl
   - Metadata: ./models/metadata_v20241028_184500.pkl
================================================================================
✅ Training completed in 45.23 seconds
================================================================================

📊 TRAINING RESULTS
================================================================================
Version: 20241028_184500
Training samples: 4000
Validation samples: 1000
Duration: 45.23s

Metrics:
  - auc_roc: 0.8542
  - auc_pr: 0.7234
  - brier_score: 0.1123
  - log_loss: 0.3456
  - precision: 0.7821
  - recall: 0.7145
  - f1_score: 0.7468
  - accuracy: 0.8920
================================================================================
```

## 🔧 Configuración Avanzada

### Hyperparameter Tuning

```python
# Grid Search sobre hiperparámetros
results = trainer.train_pipeline(
    csv_path="data.csv",
    hyperparameter_tuning=True  # Activa búsqueda de hiperparámetros
)

# Parámetros explorados:
# - n_estimators: [100, 200]
# - learning_rate: [0.05, 0.1]
# - max_depth: [3, 5, 7]
# - min_samples_split: [2, 5]
# - min_samples_leaf: [1, 2]
```

### Ajustar Contaminación de Fraude

```python
# Si esperas más fraude (10%)
results = trainer.train_pipeline(
    csv_path="data.csv",
    contamination=0.10  # 10% de anomalías esperadas
)
```

### Cambiar Split Train/Test

```python
# Usar 30% para validación
results = trainer.train_pipeline(
    csv_path="data.csv",
    test_size=0.30  # 30% validación, 70% entrenamiento
)
```

## 📁 Archivos Generados

Después del entrenamiento se generan 3 archivos:

```
models/
├── credit_risk_v20241028_184500.pkl      # Modelo de riesgo crediticio
├── fraud_detector_v20241028_184500.pkl   # Detector de fraude
└── metadata_v20241028_184500.pkl         # Metadata (features, métricas, etc)
```

### Cargar Modelo Entrenado

```python
import joblib

# Cargar modelo
model = joblib.load("models/credit_risk_v20241028_184500.pkl")

# Cargar metadata
metadata = joblib.load("models/metadata_v20241028_184500.pkl")

print(f"Version: {metadata['version']}")
print(f"AUC-ROC: {metadata['metrics']['auc_roc']:.4f}")
print(f"Features: {metadata['feature_names']}")
```

## ⚠️ Consideraciones Importantes

### 1. Tamaño Mínimo de Datos

- **Mínimo recomendado**: 1,000 muestras
- **Óptimo**: 10,000+ muestras
- **Ratio de default**: Al menos 5-10% de la clase minoritaria

### 2. Calidad de Datos

✅ **Hacer:**
- Eliminar duplicados
- Imputar valores faltantes
- Validar rangos de valores
- Balancear clases si es necesario

❌ **Evitar:**
- Datos con >20% de valores faltantes
- Features con varianza cero
- Leakage de información futura

### 3. Validación

- Usar **validación temporal** si tienes datos históricos
- Validar en **cohortes diferentes** (por región, producto, etc.)
- Monitorear **drift** después del despliegue

### 4. Reentrenamiento

- **Frecuencia**: Cada 3-6 meses
- **Trigger**: Si AUC-ROC cae >5%
- **Datos**: Usar últimos 12-24 meses

## 🔄 Pipeline de Producción

```
1. Recolectar Datos Históricos
   ↓
2. Limpiar y Validar
   ↓
3. Feature Engineering
   ↓
4. Entrenar Modelo
   ↓
5. Evaluar Métricas
   ↓
6. Si métricas OK → Guardar Modelo
   ↓
7. Cargar en Servicio (main.py)
   ↓
8. Monitorear Performance
   ↓
9. Si drift detectado → Volver a paso 1
```

## 📊 Ejemplo Completo

```python
#!/usr/bin/env python3
"""
Script completo de entrenamiento
"""

from training import ModelTrainer, create_sample_csv
import logging

logging.basicConfig(level=logging.INFO)

# 1. Generar datos de ejemplo (o usar tus datos)
csv_path = create_sample_csv(n_samples=10000)

# 2. Crear trainer
trainer = ModelTrainer(model_dir="./production_models")

# 3. Entrenar con optimización de hiperparámetros
results = trainer.train_pipeline(
    csv_path=csv_path,
    test_size=0.2,
    hyperparameter_tuning=True,  # Optimizar
    contamination=0.05
)

# 4. Verificar métricas
if results['metrics']['auc_roc'] > 0.80:
    print(f"✅ Model ready for production!")
    print(f"   Version: {results['version']}")
    print(f"   AUC-ROC: {results['metrics']['auc_roc']:.4f}")
else:
    print(f"⚠️ Model needs improvement")
    print(f"   AUC-ROC: {results['metrics']['auc_roc']:.4f} (target: >0.80)")
```

## 🆘 Troubleshooting

### Error: "Missing required columns"

**Solución**: Verifica que tu CSV tiene todas las columnas requeridas listadas arriba.

### Error: "Target must be 0 or 1"

**Solución**: La columna `default` debe contener solo valores 0 (no default) o 1 (default).

### Warning: "Low AUC-ROC"

**Soluciones**:
- Aumentar tamaño de datos
- Añadir más features relevantes
- Activar hyperparameter_tuning
- Verificar calidad de datos

### Error: "Imbalanced classes"

**Solución**: Si tienes <5% de defaults, considera:
```python
from imblearn.over_sampling import SMOTE

# Aplicar SMOTE para balancear
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
```

## 📚 Recursos Adicionales

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Gradient Boosting Guide](https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting)
- [Model Calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)

## 🎯 Próximos Pasos

1. ✅ Entrenar modelo con tus datos
2. ✅ Evaluar métricas
3. ✅ Guardar modelo
4. 📝 Actualizar `main.py` para cargar tu modelo
5. 🚀 Desplegar servicio
6. 📊 Monitorear performance
7. 🔄 Reentrenar periódicamente
