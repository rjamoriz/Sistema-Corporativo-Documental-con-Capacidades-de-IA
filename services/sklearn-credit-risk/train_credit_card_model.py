"""
Credit Card Default Prediction - Complete Training Pipeline
Procesamiento, análisis, entrenamiento y evaluación del modelo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import joblib
import warnings
warnings.filterwarnings('ignore')

# Scikit-learn
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve, auc, brier_score_loss,
    log_loss, accuracy_score, precision_score, recall_score, f1_score
)

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CreditCardModelTrainer:
    """Pipeline completo de entrenamiento para modelo de tarjetas de crédito"""
    
    def __init__(self, train_path: str, test_path: str):
        self.train_path = train_path
        self.test_path = test_path
        self.df_train = None
        self.df_test = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.model = None
        self.fraud_detector = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        
    def load_data(self):
        """Carga datos de train y test"""
        logger.info("=" * 80)
        logger.info("📂 CARGANDO DATOS")
        logger.info("=" * 80)
        
        self.df_train = pd.read_csv(self.train_path)
        self.df_test = pd.read_csv(self.test_path)
        
        logger.info(f"✅ Train: {self.df_train.shape[0]} filas, {self.df_train.shape[1]} columnas")
        logger.info(f"✅ Test: {self.df_test.shape[0]} filas, {self.df_test.shape[1]} columnas")
        logger.info(f"✅ Target (train): {self.df_train['credit_card_default'].value_counts().to_dict()}")
        logger.info(f"   - Default rate: {self.df_train['credit_card_default'].mean():.2%}")
        
        return self
    
    def exploratory_analysis(self):
        """Análisis exploratorio de datos"""
        logger.info("\n" + "=" * 80)
        logger.info("🔍 ANÁLISIS EXPLORATORIO")
        logger.info("=" * 80)
        
        # Info básica
        logger.info("\n📊 Información de columnas:")
        logger.info(f"\nColumnas: {list(self.df_train.columns)}")
        
        # Valores faltantes
        missing = self.df_train.isnull().sum()
        if missing.sum() > 0:
            logger.info("\n⚠️ Valores faltantes:")
            logger.info(missing[missing > 0].to_string())
        else:
            logger.info("\n✅ No hay valores faltantes")
        
        # Estadísticas descriptivas
        logger.info("\n📈 Estadísticas descriptivas (numéricas):")
        numeric_cols = self.df_train.select_dtypes(include=[np.number]).columns
        logger.info(self.df_train[numeric_cols].describe().to_string())
        
        # Distribución del target
        logger.info("\n🎯 Distribución del target:")
        target_dist = self.df_train['credit_card_default'].value_counts(normalize=True)
        logger.info(f"   - No Default (0): {target_dist[0]:.2%}")
        logger.info(f"   - Default (1): {target_dist[1]:.2%}")
        
        # Correlación con target
        logger.info("\n🔗 Top 10 correlaciones con target:")
        correlations = self.df_train[numeric_cols].corr()['credit_card_default'].sort_values(ascending=False)
        logger.info(correlations.head(11).to_string())  # 11 porque incluye el target mismo
        
        return self
    
    def preprocess_data(self):
        """Preprocesamiento de datos"""
        logger.info("\n" + "=" * 80)
        logger.info("🔧 PREPROCESAMIENTO DE DATOS")
        logger.info("=" * 80)
        
        # Trabajar con copias
        df_train = self.df_train.copy()
        df_test = self.df_test.copy()
        
        # 1. Eliminar customer_id y name (no son features predictivas)
        logger.info("\n🗑️ Eliminando columnas no predictivas...")
        cols_to_drop = ['customer_id', 'name']
        df_train = df_train.drop(columns=cols_to_drop, errors='ignore')
        df_test = df_test.drop(columns=cols_to_drop, errors='ignore')
        
        # 2. Manejar valores faltantes
        logger.info("🔧 Manejando valores faltantes...")
        
        # Imputar numéricos con mediana
        numeric_cols = df_train.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != 'credit_card_default']
        
        for col in numeric_cols:
            if df_train[col].isnull().sum() > 0:
                median_val = df_train[col].median()
                df_train[col].fillna(median_val, inplace=True)
                df_test[col].fillna(median_val, inplace=True)
                logger.info(f"   - {col}: imputado con mediana ({median_val:.2f})")
        
        # Imputar categóricos con moda
        categorical_cols = df_train.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df_train[col].isnull().sum() > 0:
                mode_val = df_train[col].mode()[0] if len(df_train[col].mode()) > 0 else 'Unknown'
                df_train[col].fillna(mode_val, inplace=True)
                df_test[col].fillna(mode_val, inplace=True)
                logger.info(f"   - {col}: imputado con moda ({mode_val})")
        
        # 3. Codificar variables categóricas
        logger.info("\n🔤 Codificando variables categóricas...")
        
        for col in categorical_cols:
            le = LabelEncoder()
            # Fit en train
            df_train[col] = df_train[col].astype(str)
            df_test[col] = df_test[col].astype(str)
            
            le.fit(df_train[col])
            df_train[col] = le.transform(df_train[col])
            
            # Transform en test (manejar valores no vistos)
            df_test[col] = df_test[col].apply(
                lambda x: le.transform([x])[0] if x in le.classes_ else -1
            )
            
            self.label_encoders[col] = le
            logger.info(f"   - {col}: {len(le.classes_)} categorías")
        
        # 4. Feature Engineering
        logger.info("\n⚙️ Feature Engineering...")
        
        # Ratio de uso de crédito
        df_train['credit_utilization_ratio'] = df_train['credit_limit_used(%)'] / 100.0
        df_test['credit_utilization_ratio'] = df_test['credit_limit_used(%)'] / 100.0
        
        # Ratio deuda/ingreso
        df_train['debt_to_income_ratio'] = df_train['yearly_debt_payments'] / df_train['net_yearly_income'].replace(0, 1)
        df_test['debt_to_income_ratio'] = df_test['yearly_debt_payments'] / df_test['net_yearly_income'].replace(0, 1)
        
        # Límite de crédito usado absoluto
        df_train['credit_used_amount'] = (df_train['credit_limit'] * df_train['credit_limit_used(%)']) / 100.0
        df_test['credit_used_amount'] = (df_test['credit_limit'] * df_test['credit_limit_used(%)']) / 100.0
        
        # Ingreso per cápita familiar
        df_train['income_per_family_member'] = df_train['net_yearly_income'] / df_train['total_family_members'].replace(0, 1)
        df_test['income_per_family_member'] = df_test['net_yearly_income'] / df_test['total_family_members'].replace(0, 1)
        
        # Años de empleo (convertir días a años)
        df_train['years_employed'] = df_train['no_of_days_employed'] / 365.0
        df_test['years_employed'] = df_test['no_of_days_employed'] / 365.0
        
        # Indicador de riesgo alto
        df_train['high_risk_indicator'] = (
            (df_train['prev_defaults'] > 0) | 
            (df_train['default_in_last_6months'] > 0) |
            (df_train['credit_score'] < 600)
        ).astype(int)
        df_test['high_risk_indicator'] = (
            (df_test['prev_defaults'] > 0) | 
            (df_test['default_in_last_6months'] > 0) |
            (df_test['credit_score'] < 600)
        ).astype(int)
        
        logger.info("   ✅ Features creadas:")
        logger.info("      - credit_utilization_ratio")
        logger.info("      - debt_to_income_ratio")
        logger.info("      - credit_used_amount")
        logger.info("      - income_per_family_member")
        logger.info("      - years_employed")
        logger.info("      - high_risk_indicator")
        
        # 5. Separar features y target
        target_col = 'credit_card_default'
        
        self.X_train = df_train.drop(columns=[target_col])
        self.y_train = df_train[target_col]
        
        self.X_test = df_test.drop(columns=[target_col])
        self.y_test = df_test[target_col]
        
        self.feature_names = list(self.X_train.columns)
        
        logger.info(f"\n✅ Preprocesamiento completado:")
        logger.info(f"   - Features: {len(self.feature_names)}")
        logger.info(f"   - Train samples: {len(self.X_train)}")
        logger.info(f"   - Test samples: {len(self.X_test)}")
        
        return self
    
    def train_model(self, hyperparameter_tuning: bool = False):
        """Entrena modelo de clasificación"""
        logger.info("\n" + "=" * 80)
        logger.info("🎯 ENTRENAMIENTO DEL MODELO")
        logger.info("=" * 80)
        
        if hyperparameter_tuning:
            logger.info("\n🔍 Realizando búsqueda de hiperparámetros...")
            
            param_grid = {
                'n_estimators': [100, 200],
                'learning_rate': [0.05, 0.1],
                'max_depth': [3, 5, 7],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2],
                'subsample': [0.8, 1.0]
            }
            
            base_model = GradientBoostingClassifier(random_state=42)
            grid_search = GridSearchCV(
                base_model,
                param_grid,
                cv=3,
                scoring='roc_auc',
                n_jobs=-1,
                verbose=2
            )
            
            grid_search.fit(self.X_train, self.y_train)
            self.model = grid_search.best_estimator_
            
            logger.info(f"\n✅ Mejores parámetros encontrados:")
            for param, value in grid_search.best_params_.items():
                logger.info(f"   - {param}: {value}")
            logger.info(f"   - Best CV AUC-ROC: {grid_search.best_score_:.4f}")
        else:
            logger.info("\n🎯 Entrenando con parámetros por defecto...")
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=5,
                min_samples_leaf=2,
                subsample=0.8,
                random_state=42,
                verbose=1
            )
            self.model.fit(self.X_train, self.y_train)
        
        # Calibrar probabilidades
        logger.info("\n📐 Calibrando probabilidades...")
        self.model = CalibratedClassifierCV(self.model, cv=3, method='sigmoid')
        self.model.fit(self.X_train, self.y_train)
        
        logger.info("✅ Modelo entrenado y calibrado")
        
        return self
    
    def train_fraud_detector(self, contamination: float = 0.05):
        """Entrena detector de fraude"""
        logger.info("\n🔍 Entrenando detector de fraude/anomalías...")
        
        self.fraud_detector = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        
        self.fraud_detector.fit(self.X_train)
        
        logger.info(f"✅ Detector de fraude entrenado (contamination={contamination})")
        
        return self
    
    def evaluate_model(self):
        """Evalúa el modelo en conjunto de test"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 EVALUACIÓN DEL MODELO")
        logger.info("=" * 80)
        
        # Predicciones
        y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Métricas principales
        logger.info("\n📈 Métricas de Clasificación:")
        logger.info(f"   - Accuracy: {accuracy_score(self.y_test, y_pred):.4f}")
        logger.info(f"   - Precision: {precision_score(self.y_test, y_pred):.4f}")
        logger.info(f"   - Recall: {recall_score(self.y_test, y_pred):.4f}")
        logger.info(f"   - F1-Score: {f1_score(self.y_test, y_pred):.4f}")
        logger.info(f"   - AUC-ROC: {roc_auc_score(self.y_test, y_pred_proba):.4f}")
        
        # AUC-PR
        precision, recall, _ = precision_recall_curve(self.y_test, y_pred_proba)
        auc_pr = auc(recall, precision)
        logger.info(f"   - AUC-PR: {auc_pr:.4f}")
        
        # Calibración
        brier = brier_score_loss(self.y_test, y_pred_proba)
        logloss = log_loss(self.y_test, y_pred_proba)
        logger.info(f"   - Brier Score: {brier:.4f}")
        logger.info(f"   - Log Loss: {logloss:.4f}")
        
        # Matriz de confusión
        cm = confusion_matrix(self.y_test, y_pred)
        logger.info("\n📊 Matriz de Confusión:")
        logger.info(f"   TN: {cm[0,0]:5d}  |  FP: {cm[0,1]:5d}")
        logger.info(f"   FN: {cm[1,0]:5d}  |  TP: {cm[1,1]:5d}")
        
        # Classification report
        logger.info("\n📋 Classification Report:")
        logger.info("\n" + classification_report(self.y_test, y_pred, target_names=['No Default', 'Default']))
        
        # Feature importance
        if hasattr(self.model.base_estimator, 'feature_importances_'):
            logger.info("\n🔝 Top 15 Features más importantes:")
            importances = self.model.base_estimator.feature_importances_
            indices = np.argsort(importances)[::-1][:15]
            
            for i, idx in enumerate(indices, 1):
                logger.info(f"   {i:2d}. {self.feature_names[idx]:30s}: {importances[idx]:.4f}")
        
        # Métricas del detector de fraude
        if self.fraud_detector:
            logger.info("\n🔍 Evaluación del Detector de Fraude:")
            fraud_predictions = self.fraud_detector.predict(self.X_test)
            anomaly_count = (fraud_predictions == -1).sum()
            logger.info(f"   - Anomalías detectadas: {anomaly_count} ({anomaly_count/len(self.X_test):.2%})")
        
        return {
            'accuracy': accuracy_score(self.y_test, y_pred),
            'precision': precision_score(self.y_test, y_pred),
            'recall': recall_score(self.y_test, y_pred),
            'f1_score': f1_score(self.y_test, y_pred),
            'auc_roc': roc_auc_score(self.y_test, y_pred_proba),
            'auc_pr': auc_pr,
            'brier_score': brier,
            'log_loss': logloss
        }
    
    def save_models(self, output_dir: str = "./models"):
        """Guarda modelos entrenados"""
        logger.info("\n" + "=" * 80)
        logger.info("💾 GUARDANDO MODELOS")
        logger.info("=" * 80)
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar modelo principal
        model_path = os.path.join(output_dir, f"credit_card_model_v{version}.pkl")
        joblib.dump(self.model, model_path)
        logger.info(f"✅ Modelo guardado: {model_path}")
        
        # Guardar detector de fraude
        if self.fraud_detector:
            fraud_path = os.path.join(output_dir, f"fraud_detector_v{version}.pkl")
            joblib.dump(self.fraud_detector, fraud_path)
            logger.info(f"✅ Detector de fraude guardado: {fraud_path}")
        
        # Guardar label encoders
        encoders_path = os.path.join(output_dir, f"label_encoders_v{version}.pkl")
        joblib.dump(self.label_encoders, encoders_path)
        logger.info(f"✅ Label encoders guardados: {encoders_path}")
        
        # Guardar metadata
        metadata = {
            'version': version,
            'trained_at': datetime.now().isoformat(),
            'feature_names': self.feature_names,
            'n_features': len(self.feature_names),
            'train_samples': len(self.X_train),
            'test_samples': len(self.X_test),
            'model_type': 'GradientBoostingClassifier',
            'calibrated': True
        }
        
        metadata_path = os.path.join(output_dir, f"metadata_v{version}.pkl")
        joblib.dump(metadata, metadata_path)
        logger.info(f"✅ Metadata guardada: {metadata_path}")
        
        logger.info(f"\n🎉 Todos los modelos guardados en: {output_dir}")
        logger.info(f"   Version: {version}")
        
        return version
    
    def run_full_pipeline(self, hyperparameter_tuning: bool = False):
        """Ejecuta el pipeline completo"""
        logger.info("\n" + "=" * 80)
        logger.info("🚀 INICIANDO PIPELINE COMPLETO DE ENTRENAMIENTO")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        # 1. Cargar datos
        self.load_data()
        
        # 2. Análisis exploratorio
        self.exploratory_analysis()
        
        # 3. Preprocesamiento
        self.preprocess_data()
        
        # 4. Entrenar modelo
        self.train_model(hyperparameter_tuning=hyperparameter_tuning)
        
        # 5. Entrenar detector de fraude
        self.train_fraud_detector()
        
        # 6. Evaluar
        metrics = self.evaluate_model()
        
        # 7. Guardar modelos
        version = self.save_models()
        
        # Tiempo total
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ PIPELINE COMPLETADO EXITOSAMENTE")
        logger.info("=" * 80)
        logger.info(f"⏱️  Tiempo total: {duration:.2f} segundos")
        logger.info(f"📦 Version: {version}")
        logger.info(f"🎯 AUC-ROC: {metrics['auc_roc']:.4f}")
        logger.info(f"📊 F1-Score: {metrics['f1_score']:.4f}")
        logger.info("=" * 80)
        
        return {
            'version': version,
            'metrics': metrics,
            'duration_seconds': duration
        }


def main():
    """Función principal"""
    
    # Rutas de los archivos
    train_path = "train.csv"
    test_path = "test.csv"
    
    # Crear trainer
    trainer = CreditCardModelTrainer(train_path, test_path)
    
    # Ejecutar pipeline completo
    results = trainer.run_full_pipeline(hyperparameter_tuning=False)
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    print(f"Version: {results['version']}")
    print(f"Duración: {results['duration_seconds']:.2f}s")
    print("\nMétricas:")
    for metric, value in results['metrics'].items():
        print(f"  - {metric}: {value:.4f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
