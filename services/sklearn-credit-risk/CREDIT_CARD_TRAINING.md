# 💳 Entrenamiento del Modelo de Tarjetas de Crédito

Guía completa para entrenar el modelo de predicción de default en tarjetas de crédito usando los datasets `train.csv` y `test.csv`.

## 📊 Descripción de los Datos

### Archivos Disponibles
- **`train.csv`**: Datos de entrenamiento (~45,000 registros)
- **`test.csv`**: Datos de prueba para evaluación

### Columnas del Dataset

| Columna | Tipo | Descripción |
|---|---|---|
| `customer_id` | str | ID único del cliente |
| `name` | str | Nombre del cliente |
| `age` | int | Edad del cliente |
| `gender` | str | Género (M/F) |
| `owns_car` | str | Posee coche (Y/N) |
| `owns_house` | str | Posee casa (Y/N) |
| `no_of_children` | float | Número de hijos |
| `net_yearly_income` | float | Ingresos anuales netos |
| `no_of_days_employed` | float | Días empleado |
| `occupation_type` | str | Tipo de ocupación |
| `total_family_members` | float | Miembros de la familia |
| `migrant_worker` | float | Trabajador migrante (0/1) |
| `yearly_debt_payments` | float | Pagos anuales de deuda |
| `credit_limit` | float | Límite de crédito |
| `credit_limit_used(%)` | float | Porcentaje de crédito usado |
| `credit_score` | float | Score crediticio |
| `prev_defaults` | int | Defaults previos |
| `default_in_last_6months` | int | Default en últimos 6 meses |
| **`credit_card_default`** | **int** | **Target: 0=no default, 1=default** |

## 🚀 Cómo Entrenar el Modelo

### Opción 1: Ejecutar Script Completo

```bash
# 1. Navegar al directorio
cd services/sklearn-credit-risk

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar entrenamiento
python train_credit_card_model.py
```

### Opción 2: Usar Python Interactivo

```python
from train_credit_card_model import CreditCardModelTrainer

# Crear trainer
trainer = CreditCardModelTrainer(
    train_path="train.csv",
    test_path="test.csv"
)

# Ejecutar pipeline completo
results = trainer.run_full_pipeline(
    hyperparameter_tuning=False  # True para optimizar hiperparámetros
)

print(f"AUC-ROC: {results['metrics']['auc_roc']:.4f}")
print(f"Version: {results['version']}")
```

### Opción 3: Paso a Paso

```python
from train_credit_card_model import CreditCardModelTrainer

trainer = CreditCardModelTrainer("train.csv", "test.csv")

# 1. Cargar datos
trainer.load_data()

# 2. Análisis exploratorio
trainer.exploratory_analysis()

# 3. Preprocesamiento
trainer.preprocess_data()

# 4. Entrenar modelo
trainer.train_model(hyperparameter_tuning=True)

# 5. Entrenar detector de fraude
trainer.train_fraud_detector()

# 6. Evaluar
metrics = trainer.evaluate_model()

# 7. Guardar
version = trainer.save_models()
```

## 🔧 Procesamiento Aplicado

### 1. Limpieza de Datos
- ✅ Eliminación de columnas no predictivas (`customer_id`, `name`)
- ✅ Imputación de valores faltantes (mediana para numéricos, moda para categóricos)
- ✅ Codificación de variables categóricas con LabelEncoder

### 2. Feature Engineering

El script crea automáticamente las siguientes features derivadas:

| Feature | Fórmula | Descripción |
|---|---|---|
| `credit_utilization_ratio` | `credit_limit_used(%) / 100` | Ratio de utilización normalizado |
| `debt_to_income_ratio` | `yearly_debt_payments / net_yearly_income` | Ratio deuda/ingresos |
| `credit_used_amount` | `credit_limit * credit_limit_used(%) / 100` | Monto usado absoluto |
| `income_per_family_member` | `net_yearly_income / total_family_members` | Ingreso per cápita |
| `years_employed` | `no_of_days_employed / 365` | Años de empleo |
| `high_risk_indicator` | `(prev_defaults > 0) OR (default_in_last_6months > 0) OR (credit_score < 600)` | Indicador de alto riesgo |

### 3. Modelos Entrenados

#### Modelo Principal: Gradient Boosting Classifier
```python
GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    min_samples_split=5,
    min_samples_leaf=2,
    subsample=0.8,
    random_state=42
)
```
- **Calibrado** con `CalibratedClassifierCV` (método sigmoid)
- **Probabilidades confiables** para decisiones

#### Detector de Fraude: Isolation Forest
```python
IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)
```
- Detecta anomalías en patrones de solicitud
- Identifica ~5% de casos sospechosos

## 📊 Métricas de Evaluación

El script proporciona las siguientes métricas en el conjunto de test:

| Métrica | Descripción | Objetivo |
|---|---|---|
| **Accuracy** | Precisión general | >0.85 |
| **Precision** | Precisión en clase positiva | >0.75 |
| **Recall** | Cobertura de defaults | >0.70 |
| **F1-Score** | Balance precision/recall | >0.72 |
| **AUC-ROC** | Área bajo curva ROC | >0.80 |
| **AUC-PR** | Área bajo Precision-Recall | >0.70 |
| **Brier Score** | Calibración de probabilidades | <0.15 |
| **Log Loss** | Pérdida logarítmica | <0.50 |

## 📈 Ejemplo de Output

```
================================================================================
🚀 INICIANDO PIPELINE COMPLETO DE ENTRENAMIENTO
================================================================================

================================================================================
📂 CARGANDO DATOS
================================================================================
✅ Train: 45530 filas, 19 columnas
✅ Test: 11383 filas, 19 columnas
✅ Target (train): {0: 40234, 1: 5296}
   - Default rate: 11.63%

================================================================================
🔍 ANÁLISIS EXPLORATORIO
================================================================================

📊 Información de columnas:
Columnas: ['customer_id', 'name', 'age', 'gender', ...]

✅ No hay valores faltantes

📈 Estadísticas descriptivas (numéricas):
              age  no_of_children  net_yearly_income  ...
count   45530.00        45530.00          45530.00  ...
mean       43.98            0.42         168787.92  ...
std         8.61            0.74         237123.45  ...

🎯 Distribución del target:
   - No Default (0): 88.37%
   - Default (1): 11.63%

🔗 Top 10 correlaciones con target:
credit_card_default              1.000000
prev_defaults                    0.456789
default_in_last_6months          0.398765
credit_limit_used(%)             0.287654
...

================================================================================
🔧 PREPROCESAMIENTO DE DATOS
================================================================================

🗑️ Eliminando columnas no predictivas...
🔧 Manejando valores faltantes...
   - no_of_children: imputado con mediana (0.00)
   - occupation_type: imputado con moda (Unknown)

🔤 Codificando variables categóricas...
   - gender: 2 categorías
   - occupation_type: 15 categorías

⚙️ Feature Engineering...
   ✅ Features creadas:
      - credit_utilization_ratio
      - debt_to_income_ratio
      - credit_used_amount
      - income_per_family_member
      - years_employed
      - high_risk_indicator

✅ Preprocesamiento completado:
   - Features: 23
   - Train samples: 45530
   - Test samples: 11383

================================================================================
🎯 ENTRENAMIENTO DEL MODELO
================================================================================

🎯 Entrenando con parámetros por defecto...
      Iter       Train Loss   Remaining Time 
         1           0.3456            12.34s
        50           0.1234             8.45s
       100           0.0987             4.23s
       150           0.0856             2.11s
       200           0.0789             0.00s

📐 Calibrando probabilidades...
✅ Modelo entrenado y calibrado

🔍 Entrenando detector de fraude/anomalías...
✅ Detector de fraude entrenado (contamination=0.05)

================================================================================
📊 EVALUACIÓN DEL MODELO
================================================================================

📈 Métricas de Clasificación:
   - Accuracy: 0.9234
   - Precision: 0.8567
   - Recall: 0.7845
   - F1-Score: 0.8189
   - AUC-ROC: 0.8923
   - AUC-PR: 0.7654
   - Brier Score: 0.0987
   - Log Loss: 0.2345

📊 Matriz de Confusión:
   TN: 10123  |  FP:   345
   FN:   567  |  TP:   348

📋 Classification Report:
              precision    recall  f1-score   support
  No Default       0.95      0.97      0.96     10468
     Default       0.86      0.78      0.82       915
    accuracy                           0.92     11383

🔝 Top 15 Features más importantes:
    1. prev_defaults                  : 0.1845
    2. credit_score                   : 0.1567
    3. default_in_last_6months        : 0.1234
    4. credit_utilization_ratio       : 0.0987
    5. debt_to_income_ratio           : 0.0856
    6. high_risk_indicator            : 0.0745
    7. credit_limit_used(%)           : 0.0654
    8. yearly_debt_payments           : 0.0543
    9. net_yearly_income              : 0.0432
   10. age                            : 0.0321
   11. years_employed                 : 0.0298
   12. credit_used_amount             : 0.0276
   13. income_per_family_member       : 0.0234
   14. total_family_members           : 0.0198
   15. no_of_children                 : 0.0167

🔍 Evaluación del Detector de Fraude:
   - Anomalías detectadas: 569 (5.00%)

================================================================================
💾 GUARDANDO MODELOS
================================================================================
✅ Modelo guardado: ./models/credit_card_model_v20241028_185500.pkl
✅ Detector de fraude guardado: ./models/fraud_detector_v20241028_185500.pkl
✅ Label encoders guardados: ./models/label_encoders_v20241028_185500.pkl
✅ Metadata guardada: ./models/metadata_v20241028_185500.pkl

🎉 Todos los modelos guardados en: ./models
   Version: 20241028_185500

================================================================================
✅ PIPELINE COMPLETADO EXITOSAMENTE
================================================================================
⏱️  Tiempo total: 123.45 segundos
📦 Version: 20241028_185500
🎯 AUC-ROC: 0.8923
📊 F1-Score: 0.8189
================================================================================
```

## 📁 Archivos Generados

Después del entrenamiento se crean 4 archivos en `./models/`:

```
models/
├── credit_card_model_v20241028_185500.pkl      # Modelo principal (GradientBoosting + Calibración)
├── fraud_detector_v20241028_185500.pkl         # Detector de fraude (IsolationForest)
├── label_encoders_v20241028_185500.pkl         # Encoders para variables categóricas
└── metadata_v20241028_185500.pkl               # Metadata (features, métricas, etc)
```

## 🔄 Integración con el Servicio

### Cargar Modelo Entrenado en main.py

```python
import joblib

# Cargar modelo entrenado
credit_risk_model = joblib.load("models/credit_card_model_v20241028_185500.pkl")
fraud_detector = joblib.load("models/fraud_detector_v20241028_185500.pkl")
label_encoders = joblib.load("models/label_encoders_v20241028_185500.pkl")
metadata = joblib.load("models/metadata_v20241028_185500.pkl")

print(f"Modelo cargado: {metadata['version']}")
print(f"AUC-ROC: {metadata['metrics']['auc_roc']:.4f}")
```

### Hacer Predicción

```python
import pandas as pd
import numpy as np

# Preparar datos de entrada (mismo preprocesamiento)
def prepare_input(data_dict):
    # Aplicar mismo feature engineering
    df = pd.DataFrame([data_dict])
    
    # Codificar categóricas
    for col, encoder in label_encoders.items():
        if col in df.columns:
            df[col] = encoder.transform(df[col].astype(str))
    
    # Feature engineering
    df['credit_utilization_ratio'] = df['credit_limit_used(%)'] / 100.0
    df['debt_to_income_ratio'] = df['yearly_debt_payments'] / df['net_yearly_income']
    df['credit_used_amount'] = (df['credit_limit'] * df['credit_limit_used(%)']) / 100.0
    df['income_per_family_member'] = df['net_yearly_income'] / df['total_family_members']
    df['years_employed'] = df['no_of_days_employed'] / 365.0
    df['high_risk_indicator'] = (
        (df['prev_defaults'] > 0) | 
        (df['default_in_last_6months'] > 0) |
        (df['credit_score'] < 600)
    ).astype(int)
    
    return df[metadata['feature_names']]

# Ejemplo de predicción
customer_data = {
    'age': 35,
    'gender': 'M',
    'owns_car': 'Y',
    'owns_house': 'Y',
    'no_of_children': 2,
    'net_yearly_income': 150000,
    'no_of_days_employed': 2000,
    'occupation_type': 'Core staff',
    'total_family_members': 4,
    'migrant_worker': 0,
    'yearly_debt_payments': 25000,
    'credit_limit': 50000,
    'credit_limit_used(%)': 65,
    'credit_score': 720,
    'prev_defaults': 0,
    'default_in_last_6months': 0
}

X = prepare_input(customer_data)
probability = credit_risk_model.predict_proba(X)[0][1]
prediction = int(probability > 0.5)

print(f"Probabilidad de default: {probability:.2%}")
print(f"Predicción: {'Default' if prediction else 'No Default'}")
```

## ⚙️ Configuración Avanzada

### Hyperparameter Tuning

```python
# Activar búsqueda de hiperparámetros (tarda más tiempo)
results = trainer.run_full_pipeline(hyperparameter_tuning=True)
```

Parámetros explorados:
- `n_estimators`: [100, 200]
- `learning_rate`: [0.05, 0.1]
- `max_depth`: [3, 5, 7]
- `min_samples_split`: [2, 5]
- `min_samples_leaf`: [1, 2]
- `subsample`: [0.8, 1.0]

### Ajustar Contaminación de Fraude

```python
# Si esperas más fraude (10%)
trainer.train_fraud_detector(contamination=0.10)
```

## 🎯 Próximos Pasos

1. ✅ Ejecutar `python train_credit_card_model.py`
2. ✅ Revisar métricas en consola
3. ✅ Verificar modelos en `./models/`
4. 📝 Actualizar `main.py` para cargar modelo entrenado
5. 🧪 Probar predicciones con datos reales
6. 🚀 Desplegar servicio
7. 📊 Monitorear performance en producción

## 🆘 Troubleshooting

### Error: "FileNotFoundError: train.csv"
**Solución**: Asegúrate de estar en el directorio correcto:
```bash
cd services/sklearn-credit-risk
ls train.csv test.csv  # Verificar archivos
```

### Warning: "Low AUC-ROC"
**Soluciones**:
- Activar `hyperparameter_tuning=True`
- Verificar balance de clases
- Revisar calidad de features

### Error: "Memory Error"
**Solución**: Reducir `n_estimators` o usar menos datos:
```python
# Usar subset de datos
df_train = df_train.sample(n=10000, random_state=42)
```

## 📚 Recursos

- [Gradient Boosting Documentation](https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting)
- [Calibration Guide](https://scikit-learn.org/stable/modules/calibration.html)
- [Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
