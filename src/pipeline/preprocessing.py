# src/pipeline/preprocessing.py

"""
Real-Time Cyber Threat Detection and Response System: Data Preprocessing Pipeline

This module handles data preprocessing for machine learning tasks, including:
- Feature engineering
- Scaling
- Encoding
- Validation checks
- Error handling
- Logging

Production-grade implementation with advanced patterns, optimization, and best practices.
"""

import os
import logging
import json
from typing import Any, Dict, List, Tuple, Union
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.exceptions import NotFittedError
import numpy as np
import pandas as pd

# ===========================
# Configuration Management
# ===========================

class Config:
    """Configuration management for preprocessing pipeline."""
    DEFAULT_NUMERIC_FEATURES = ["feature1", "feature2", "feature3"]
    DEFAULT_CATEGORICAL_FEATURES = ["category1", "category2"]
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "preprocessing.log")

# ===========================
# Logging Setup
# ===========================

logging.basicConfig(
    level=Config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===========================
# Custom Exceptions
# ===========================

class PreprocessingError(Exception):
    """Custom exception for preprocessing errors."""
    pass

# ===========================
# Utility Functions
# ===========================

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> None:
    """
    Validate that the dataframe contains the required columns.
    Raises:
        PreprocessingError: If validation fails.
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        raise PreprocessingError(f"Missing required columns: {missing_columns}")

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the dataframe.
    Returns:
        pd.DataFrame: Dataframe with missing values handled.
    """
    logger.info("Handling missing values...")
    return df.fillna(method="ffill").fillna(method="bfill")

# ===========================
# Preprocessing Pipeline
# ===========================

class PreprocessingPipeline:
    """
    Production-grade preprocessing pipeline for real-time cyber threat detection.
    """

    def __init__(self, numeric_features: List[str], categorical_features: List[str]) -> None:
        """
        Initialize the preprocessing pipeline.
        Args:
            numeric_features (List[str]): List of numeric feature names.
            categorical_features (List[str]): List of categorical feature names.
        """
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.pipeline: Pipeline = self._build_pipeline()
        logger.info("Preprocessing pipeline initialized.")

    def _build_pipeline(self) -> Pipeline:
        """
        Build the preprocessing pipeline.
        Returns:
            Pipeline: Sklearn pipeline for preprocessing.
        """
        logger.info("Building preprocessing pipeline...")
        try:
            numeric_transformer = StandardScaler()
            categorical_transformer = OneHotEncoder(handle_unknown="ignore")

            preprocessor = ColumnTransformer(
                transformers=[
                    ("num", numeric_transformer, self.numeric_features),
                    ("cat", categorical_transformer, self.categorical_features)
                ]
            )

            pipeline = Pipeline(steps=[("preprocessor", preprocessor)])
            logger.info("Pipeline successfully built.")
            return pipeline
        except Exception as e:
            logger.exception("Error building pipeline.")
            raise PreprocessingError(f"Error building pipeline: {str(e)}")

    def fit(self, X: pd.DataFrame) -> None:
        """
        Fit the preprocessing pipeline to the data.
        Args:
            X (pd.DataFrame): Input dataframe.
        """
        logger.info("Fitting preprocessing pipeline...")
        try:
            validate_dataframe(X, self.numeric_features + self.categorical_features)
            X = handle_missing_values(X)
            self.pipeline.fit(X)
            logger.info("Pipeline successfully fitted.")
        except Exception as e:
            logger.exception("Error fitting pipeline.")
            raise PreprocessingError(f"Error fitting pipeline: {str(e)}")

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform the data using the fitted pipeline.
        Args:
            X (pd.DataFrame): Input dataframe.
        Returns:
            np.ndarray: Transformed data.
        """
        logger.info("Transforming data using preprocessing pipeline...")
        try:
            validate_dataframe(X, self.numeric_features + self.categorical_features)
            X = handle_missing_values(X)
            transformed_data = self.pipeline.transform(X)
            logger.info("Data successfully transformed.")
            return transformed_data
        except NotFittedError:
            logger.error("Pipeline has not been fitted yet.")
            raise PreprocessingError("Pipeline has not been fitted yet.")
        except Exception as e:
            logger.exception("Error transforming data.")
            raise PreprocessingError(f"Error transforming data: {str(e)}")

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Fit and transform the data using the pipeline.
        Args:
            X (pd.DataFrame): Input dataframe.
        Returns:
            np.ndarray: Transformed data.
        """
        logger.info("Fitting and transforming data using preprocessing pipeline...")
        try:
            self.fit(X)
            return self.transform(X)
        except Exception as e:
            logger.exception("Error in fit_transform.")
            raise PreprocessingError(f"Error in fit_transform: {str(e)}")

# ===========================
# Monitoring and Testing
# ===========================

def monitor_pipeline(pipeline: PreprocessingPipeline, test_data: pd.DataFrame) -> None:
    """
    Monitor the pipeline with test data to ensure functionality.
    Args:
        pipeline (PreprocessingPipeline): Preprocessing pipeline instance.
        test_data (pd.DataFrame): Test dataframe.
    """
    logger.info("Monitoring pipeline...")
    try:
        transformed_data = pipeline.fit_transform(test_data)
        logger.info(f"Pipeline monitoring successful. Transformed data shape: {transformed_data.shape}")
    except Exception as e:
        logger.exception("Pipeline monitoring failed.")
        raise PreprocessingError(f"Pipeline monitoring failed: {str(e)}")

# ===========================
# Main Execution
# ===========================

if __name__ == "__main__":
    # Example usage
    logger.info("Starting preprocessing pipeline...")

    # Example configuration
    numeric_features = Config.DEFAULT_NUMERIC_FEATURES
    categorical_features = Config.DEFAULT_CATEGORICAL_FEATURES

    # Example data
    data = pd.DataFrame({
        "feature1": [1.0, 2.0, np.nan],
        "feature2": [3.0, 4.0, 5.0],
        "feature3": [6.0, np.nan, 8.0],
        "category1": ["A", "B", "A"],
        "category2": ["X", "Y", "Z"]
    })

    # Initialize pipeline
    pipeline = PreprocessingPipeline(numeric_features, categorical_features)

    # Monitor pipeline
    monitor_pipeline(pipeline, data)

    logger.info("Preprocessing pipeline execution completed.")