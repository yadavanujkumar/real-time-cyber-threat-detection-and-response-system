# src/pipeline/training.py

"""
Real-Time Cyber Threat Detection and Response System - Model Training Module

This module handles the training pipeline for machine learning models, including:
- Cross-validation setup
- Hyperparameter tuning
- Evaluation metrics
- Model versioning and checkpointing
- Early stopping for efficient training

Author: Senior Software Engineer - Production Systems Specialist
"""

import os
import logging
import json
from typing import Any, Dict, Tuple, List
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import NotFittedError
import datetime

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("training_pipeline")

# Configuration management
class Config:
    MODEL_DIR = os.getenv("MODEL_DIR", "models/")
    CHECKPOINT_DIR = os.getenv("CHECKPOINT_DIR", "checkpoints/")
    RANDOM_SEED = int(os.getenv("RANDOM_SEED", 42))
    TEST_SIZE = float(os.getenv("TEST_SIZE", 0.2))
    CV_FOLDS = int(os.getenv("CV_FOLDS", 5))
    EARLY_STOPPING_ROUNDS = int(os.getenv("EARLY_STOPPING_ROUNDS", 10))

# Utility functions
def save_model(model: Any, version: str) -> None:
    """
    Save the model with versioning.
    """
    os.makedirs(Config.MODEL_DIR, exist_ok=True)
    model_path = os.path.join(Config.MODEL_DIR, f"model_{version}.joblib")
    joblib.dump(model, model_path)
    logger.info(f"Model saved at {model_path}")

def load_model(version: str) -> Any:
    """
    Load a specific version of the model.
    """
    model_path = os.path.join(Config.MODEL_DIR, f"model_{version}.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model version {version} not found at {model_path}")
    model = joblib.load(model_path)
    logger.info(f"Model loaded from {model_path}")
    return model

def save_checkpoint(model: Any, epoch: int) -> None:
    """
    Save a checkpoint during training.
    """
    os.makedirs(Config.CHECKPOINT_DIR, exist_ok=True)
    checkpoint_path = os.path.join(Config.CHECKPOINT_DIR, f"checkpoint_epoch_{epoch}.joblib")
    joblib.dump(model, checkpoint_path)
    logger.info(f"Checkpoint saved at {checkpoint_path}")

def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Evaluate the model using multiple metrics.
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="binary"),
        "recall": recall_score(y_true, y_pred, average="binary"),
        "f1_score": f1_score(y_true, y_pred, average="binary"),
        "roc_auc": roc_auc_score(y_true, y_pred),
    }
    logger.info(f"Evaluation metrics: {metrics}")
    return metrics

# Training pipeline
class ModelTrainer:
    def __init__(self, config: Config):
        self.config = config
        self.model = None
        self.best_params = None

    def train(
        self, X: np.ndarray, y: np.ndarray, param_grid: Dict[str, List[Any]]
    ) -> Tuple[Any, Dict[str, float]]:
        """
        Train the model with cross-validation and hyperparameter tuning.
        """
        logger.info("Starting training pipeline...")
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=self.config.TEST_SIZE, random_state=self.config.RANDOM_SEED
        )
        logger.info(f"Data split into train and validation sets. Test size: {self.config.TEST_SIZE}")

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", RandomForestClassifier(random_state=self.config.RANDOM_SEED)),
        ])

        grid_search = GridSearchCV(
            estimator=pipeline,
            param_grid=param_grid,
            cv=self.config.CV_FOLDS,
            scoring="f1",
            verbose=2,
            n_jobs=-1,
        )

        logger.info("Performing hyperparameter tuning...")
        grid_search.fit(X_train, y_train)
        self.best_params = grid_search.best_params_
        logger.info(f"Best hyperparameters: {self.best_params}")

        self.model = grid_search.best_estimator_

        # Early stopping logic
        best_score = -np.inf
        no_improvement_count = 0
        for epoch in range(1, 101):  # Max epochs
            logger.info(f"Epoch {epoch}...")
            self.model.fit(X_train, y_train)
            y_val_pred = self.model.predict(X_val)
            metrics = evaluate_model(y_val, y_val_pred)

            if metrics["f1_score"] > best_score:
                best_score = metrics["f1_score"]
                save_checkpoint(self.model, epoch)
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            if no_improvement_count >= self.config.EARLY_STOPPING_ROUNDS:
                logger.info("Early stopping triggered.")
                break

        logger.info("Training completed.")
        return self.model, metrics

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict using the trained model.
        """
        if not self.model:
            raise NotFittedError("Model is not trained yet.")
        return self.model.predict(X)

# Main execution
if __name__ == "__main__":
    # Example usage
    logger.info("Initializing training pipeline...")
    config = Config()
    trainer = ModelTrainer(config)

    # Example dataset (replace with actual data loading logic)
    X = np.random.rand(1000, 20)
    y = np.random.randint(0, 2, 1000)

    # Hyperparameter grid
    param_grid = {
        "classifier__n_estimators": [50, 100, 200],
        "classifier__max_depth": [None, 10, 20],
        "classifier__min_samples_split": [2, 5, 10],
    }

    model, metrics = trainer.train(X, y, param_grid)
    save_model(model, version=datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    logger.info("Training pipeline completed successfully.")