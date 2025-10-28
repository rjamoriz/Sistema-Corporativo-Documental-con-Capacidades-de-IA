"""
Training Module for Credit Risk Model
Permite entrenar modelos con datos CSV
"""

import os
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import joblib

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc,
    classification_report, confusion_matrix,
    brier_score_loss, log_loss
)

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Entrenador de modelos de riesgo crediticio"""
    
    # Columnas esperadas en el CSV
    REQUIRED_COLUMNS = {
        # Estructuradas
        'age', 'income', 'employment_years',
        'credit_history_months', 'num_previous_loans', 'num_defaults',
        'loan_amount', 'loan_duration_months',
        'customer_tenure_months', 'num_products', 'avg_balance',
        
        # Target
        'default'  # 0 = no default, 1 = default
    }
    
    OPTIONAL_COLUMNS = {
        # No estructuradas (opcionales)
        'external_credit_score',
        'doc_sentiment_score', 'risk_clauses_count',
        'inconsistencies_detected', 'payment_delay_mentions',
        'legal_issues_mentions', 'restructuring_mentions',
        'document_completeness', 'document_quality_score'
    }
    
    def __init__(self, model_dir: str = "./models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def load_and_validate_data(self, csv_path: str) -> pd.DataFrame:
        """Carga y valida datos del CSV"""
        logger.info(f"📂 Loading data from {csv_path}")
        
        # Leer CSV
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        
        # Verificar columnas requeridas
        missing_cols = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise ValueError(f"❌ Missing required columns: {missing_cols}")
        
        # Verificar target
        if 'default' not in df.columns:
            raise ValueError("❌ Target column 'default' not found")
        
        # Verificar valores del target
        unique_targets = df['default'].unique()
        if not set(unique_targets).issubset({0, 1}):
            raise ValueError(f"❌ Target must be 0 or 1, found: {unique_targets}")
        
        logger.info(f"✅ Data validation passed")
        logger.info(f"   - Default rate: {df['default'].mean():.2%}")
        logger.info(f"   - Samples: {len(df)} (Default: {df['default'].sum()}, No Default: {(~df['default'].astype(bool)).sum()})")
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crea features derivadas"""
        logger.info("🔧 Engineering features...")
        
        df = df.copy()
        
        # Ratios importantes
        df['debt_to_income_ratio'] = df['loan_amount'] / df['income'].replace(0, 1)
        
        monthly_payment = df['loan_amount'] / df['loan_duration_months'].replace(0, 1)
        df['payment_to_income_ratio'] = (monthly_payment * 12) / df['income'].replace(0, 1)
        
        # Transformaciones logarítmicas
        df['log_income'] = np.log1p(df['income'])
        df['log_loan_amount'] = np.log1p(df['loan_amount'])
        df['log_avg_balance'] = np.log1p(df['avg_balance'])
        
        # Normalizar edad y años de empleo
        df['age_norm'] = df['age'] / 100.0
        df['employment_years_norm'] = df['employment_years'] / 40.0
        
        # Normalizar historial
        df['credit_history_norm'] = df['credit_history_months'] / 120.0
        df['customer_tenure_norm'] = df['customer_tenure_months'] / 120.0
        
        # Features no estructuradas (si existen)
        if 'doc_sentiment_score' in df.columns:
            df['doc_sentiment_norm'] = (df['doc_sentiment_score'] + 1) / 2.0
        else:
            df['doc_sentiment_norm'] = 0.5
        
        # Indicadores de riesgo documental
        for col in ['risk_clauses_count', 'inconsistencies_detected', 
                    'payment_delay_mentions', 'legal_issues_mentions', 
                    'restructuring_mentions']:
            if col not in df.columns:
                df[col] = 0
        
        # Calidad documental
        for col in ['document_completeness', 'document_quality_score']:
            if col not in df.columns:
                df[col] = 0.5
        
        # Score externo
        if 'external_credit_score' in df.columns:
            df['external_score_norm'] = (df['external_credit_score'] - 300) / 550.0
        else:
            df['external_score_norm'] = 0.5
        
        logger.info(f"✅ Features engineered: {len(df.columns)} total columns")
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepara features para entrenamiento"""
        logger.info("📊 Preparing features...")
        
        # Features finales para el modelo
        feature_cols = [
            'age_norm', 'log_income', 'employment_years_norm',
            'credit_history_norm', 'num_previous_loans', 'num_defaults',
            'external_score_norm', 'log_loan_amount', 'loan_duration_months',
            'debt_to_income_ratio', 'payment_to_income_ratio',
            'customer_tenure_norm', 'num_products', 'log_avg_balance',
            'doc_sentiment_norm', 'risk_clauses_count', 'inconsistencies_detected',
            'payment_delay_mentions', 'legal_issues_mentions', 'restructuring_mentions',
            'document_completeness', 'document_quality_score'
        ]
        
        X = df[feature_cols].values
        y = df['default'].values
        
        logger.info(f"✅ Features prepared: {X.shape}")
        logger.info(f"   - Features: {len(feature_cols)}")
        logger.info(f"   - Samples: {len(X)}")
        
        return X, y, feature_cols
    
    def train_credit_risk_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        hyperparameter_tuning: bool = False
    ) -> Tuple[Any, Dict[str, float]]:
        """Entrena modelo de riesgo crediticio"""
        logger.info("🎯 Training credit risk model...")
        
        if hyperparameter_tuning:
            logger.info("🔍 Performing hyperparameter tuning...")
            
            param_grid = {
                'n_estimators': [100, 200],
                'learning_rate': [0.05, 0.1],
                'max_depth': [3, 5, 7],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2]
            }
            
            base_model = GradientBoostingClassifier(random_state=42)
            grid_search = GridSearchCV(
                base_model,
                param_grid,
                cv=3,
                scoring='roc_auc',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train, y_train)
            model = grid_search.best_estimator_
            
            logger.info(f"✅ Best parameters: {grid_search.best_params_}")
            logger.info(f"✅ Best CV score: {grid_search.best_score_:.4f}")
        else:
            # Modelo con parámetros por defecto
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42
            )
            
            model.fit(X_train, y_train)
        
        # Calibrar probabilidades
        logger.info("📐 Calibrating probabilities...")
        calibrated_model = CalibratedClassifierCV(model, cv=3, method='sigmoid')
        calibrated_model.fit(X_train, y_train)
        
        # Evaluar
        metrics = self._evaluate_model(calibrated_model, X_val, y_val)
        
        logger.info("✅ Credit risk model trained")
        logger.info(f"   - AUC-ROC: {metrics['auc_roc']:.4f}")
        logger.info(f"   - AUC-PR: {metrics['auc_pr']:.4f}")
        logger.info(f"   - Brier Score: {metrics['brier_score']:.4f}")
        
        return calibrated_model, metrics
    
    def train_fraud_detector(
        self,
        X_train: np.ndarray,
        contamination: float = 0.05
    ) -> IsolationForest:
        """Entrena detector de fraude"""
        logger.info("🔍 Training fraud detector...")
        
        detector = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        
        detector.fit(X_train)
        
        logger.info(f"✅ Fraud detector trained (contamination={contamination})")
        
        return detector
    
    def _evaluate_model(
        self,
        model: Any,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> Dict[str, float]:
        """Evalúa modelo en conjunto de validación"""
        
        # Predicciones
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Métricas
        auc_roc = roc_auc_score(y_val, y_pred_proba)
        
        precision, recall, _ = precision_recall_curve(y_val, y_pred_proba)
        auc_pr = auc(recall, precision)
        
        brier = brier_score_loss(y_val, y_pred_proba)
        logloss = log_loss(y_val, y_pred_proba)
        
        # Classification report
        report = classification_report(y_val, y_pred, output_dict=True)
        
        return {
            'auc_roc': auc_roc,
            'auc_pr': auc_pr,
            'brier_score': brier,
            'log_loss': logloss,
            'precision': report['1']['precision'],
            'recall': report['1']['recall'],
            'f1_score': report['1']['f1-score'],
            'accuracy': report['accuracy']
        }
    
    def save_models(
        self,
        credit_risk_model: Any,
        fraud_detector: Any,
        feature_names: List[str],
        metrics: Dict[str, float],
        version: str = None
    ) -> str:
        """Guarda modelos entrenados"""
        
        if version is None:
            version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        model_path = os.path.join(self.model_dir, f"credit_risk_v{version}.pkl")
        fraud_path = os.path.join(self.model_dir, f"fraud_detector_v{version}.pkl")
        metadata_path = os.path.join(self.model_dir, f"metadata_v{version}.pkl")
        
        logger.info(f"💾 Saving models to {self.model_dir}")
        
        # Guardar modelos
        joblib.dump(credit_risk_model, model_path)
        joblib.dump(fraud_detector, fraud_path)
        
        # Guardar metadata
        metadata = {
            'version': version,
            'trained_at': datetime.utcnow().isoformat(),
            'feature_names': feature_names,
            'metrics': metrics,
            'model_type': 'GradientBoostingClassifier',
            'calibrated': True
        }
        joblib.dump(metadata, metadata_path)
        
        logger.info(f"✅ Models saved:")
        logger.info(f"   - Credit Risk: {model_path}")
        logger.info(f"   - Fraud Detector: {fraud_path}")
        logger.info(f"   - Metadata: {metadata_path}")
        
        return version
    
    def train_pipeline(
        self,
        csv_path: str,
        test_size: float = 0.2,
        hyperparameter_tuning: bool = False,
        contamination: float = 0.05
    ) -> Dict[str, Any]:
        """Pipeline completo de entrenamiento"""
        
        logger.info("=" * 80)
        logger.info("🚀 Starting training pipeline")
        logger.info("=" * 80)
        
        start_time = datetime.utcnow()
        
        # 1. Cargar y validar datos
        df = self.load_and_validate_data(csv_path)
        
        # 2. Feature engineering
        df = self.engineer_features(df)
        
        # 3. Preparar features
        X, y, feature_names = self.prepare_features(df)
        
        # 4. Split train/validation
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=test_size,
            random_state=42,
            stratify=y
        )
        
        logger.info(f"📊 Data split:")
        logger.info(f"   - Train: {len(X_train)} samples ({y_train.mean():.2%} default)")
        logger.info(f"   - Val: {len(X_val)} samples ({y_val.mean():.2%} default)")
        
        # 5. Entrenar modelo de riesgo
        credit_risk_model, metrics = self.train_credit_risk_model(
            X_train, y_train, X_val, y_val,
            hyperparameter_tuning=hyperparameter_tuning
        )
        
        # 6. Entrenar detector de fraude
        fraud_detector = self.train_fraud_detector(X_train, contamination)
        
        # 7. Guardar modelos
        version = self.save_models(
            credit_risk_model,
            fraud_detector,
            feature_names,
            metrics
        )
        
        # Tiempo total
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info(f"✅ Training completed in {duration:.2f} seconds")
        logger.info("=" * 80)
        
        return {
            'version': version,
            'metrics': metrics,
            'feature_names': feature_names,
            'training_samples': len(X_train),
            'validation_samples': len(X_val),
            'training_duration_seconds': duration
        }


def create_sample_csv(output_path: str = "sample_training_data.csv", n_samples: int = 1000):
    """Crea un CSV de ejemplo para entrenamiento"""
    
    logger.info(f"📝 Creating sample CSV with {n_samples} samples...")
    
    np.random.seed(42)
    
    # Generar datos sintéticos
    data = {
        # Demográficas
        'age': np.random.randint(18, 70, n_samples),
        'income': np.random.lognormal(10.5, 0.5, n_samples),
        'employment_years': np.random.randint(0, 40, n_samples),
        
        # Historial crediticio
        'credit_history_months': np.random.randint(0, 120, n_samples),
        'num_previous_loans': np.random.randint(0, 10, n_samples),
        'num_defaults': np.random.choice([0, 1, 2], n_samples, p=[0.7, 0.2, 0.1]),
        'external_credit_score': np.random.randint(300, 850, n_samples),
        
        # Operación actual
        'loan_amount': np.random.lognormal(10, 0.8, n_samples),
        'loan_duration_months': np.random.choice([12, 24, 36, 48, 60, 84], n_samples),
        
        # Relación con entidad
        'customer_tenure_months': np.random.randint(0, 120, n_samples),
        'num_products': np.random.randint(0, 5, n_samples),
        'avg_balance': np.random.lognormal(8, 1, n_samples),
        
        # Features no estructuradas
        'doc_sentiment_score': np.random.uniform(-1, 1, n_samples),
        'risk_clauses_count': np.random.poisson(2, n_samples),
        'inconsistencies_detected': np.random.poisson(0.5, n_samples),
        'payment_delay_mentions': np.random.poisson(0.3, n_samples),
        'legal_issues_mentions': np.random.poisson(0.1, n_samples),
        'restructuring_mentions': np.random.poisson(0.2, n_samples),
        'document_completeness': np.random.beta(8, 2, n_samples),
        'document_quality_score': np.random.beta(7, 2, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generar target basado en features (simulación realista)
    risk_score = (
        (df['num_defaults'] * 0.3) +
        (df['risk_clauses_count'] / 10 * 0.2) +
        ((df['loan_amount'] / df['income']) * 0.2) +
        ((850 - df['external_credit_score']) / 550 * 0.2) +
        (df['payment_delay_mentions'] / 5 * 0.1)
    )
    
    # Convertir a probabilidad
    prob_default = 1 / (1 + np.exp(-2 * (risk_score - 0.5)))
    
    # Generar target
    df['default'] = (np.random.random(n_samples) < prob_default).astype(int)
    
    # Guardar
    df.to_csv(output_path, index=False)
    
    logger.info(f"✅ Sample CSV created: {output_path}")
    logger.info(f"   - Samples: {len(df)}")
    logger.info(f"   - Default rate: {df['default'].mean():.2%}")
    logger.info(f"   - Columns: {len(df.columns)}")
    
    return output_path


if __name__ == "__main__":
    # Ejemplo de uso
    logging.basicConfig(level=logging.INFO)
    
    # 1. Crear CSV de ejemplo
    csv_path = create_sample_csv(n_samples=5000)
    
    # 2. Entrenar modelos
    trainer = ModelTrainer()
    results = trainer.train_pipeline(
        csv_path=csv_path,
        test_size=0.2,
        hyperparameter_tuning=False,
        contamination=0.05
    )
    
    print("\n" + "=" * 80)
    print("📊 TRAINING RESULTS")
    print("=" * 80)
    print(f"Version: {results['version']}")
    print(f"Training samples: {results['training_samples']}")
    print(f"Validation samples: {results['validation_samples']}")
    print(f"Duration: {results['training_duration_seconds']:.2f}s")
    print("\nMetrics:")
    for metric, value in results['metrics'].items():
        print(f"  - {metric}: {value:.4f}")
    print("=" * 80)
