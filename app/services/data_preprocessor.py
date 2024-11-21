import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, List, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from app.models.models import InventoryTransaction
from app.schemas import schemas

logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self):
        self.scalers: Dict[str, StandardScaler] = {}
        self.label_encoders: Dict[str, LabelEncoder] = {}
        
    def preprocess_transaction_data(
        self,
        db: Session,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """Preprocess transaction data"""
        try:
            # Create copy of data
            df = data.copy()
            
            # Handle missing values
            df = self._handle_missing_values(df)
            
            # Encode categorical variables
            df = self._encode_categorical_variables(df)
            
            # Scale numerical features
            df = self._scale_numerical_features(df)
            
            # Add derived features
            df = self._add_derived_features(df, db)
            
            logger.info("Data preprocessing completed successfully")
            return df
            
        except Exception as e:
            logger.error(f"Error in data preprocessing: {str(e)}")
            raise
            
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        # Fill numeric columns with median
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
        
        # Fill categorical columns with mode
        categorical_columns = df.select_dtypes(exclude=[np.number]).columns
        df[categorical_columns] = df[categorical_columns].fillna(df[categorical_columns].mode().iloc[0])
        
        return df
        
    def _encode_categorical_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables"""
        categorical_columns = ['category', 'supplier', 'transaction_type']
        
        for column in categorical_columns:
            if column in df.columns:
                if column not in self.label_encoders:
                    self.label_encoders[column] = LabelEncoder()
                    df[f'{column}_encoded'] = self.label_encoders[column].fit_transform(df[column])
                else:
                    df[f'{column}_encoded'] = self.label_encoders[column].transform(df[column])
        
        return df
        
    def _scale_numerical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features"""
        numerical_features = ['quantity', 'unit_price', 'total_value']
        
        if 'numerical_scaler' not in self.scalers:
            self.scalers['numerical_scaler'] = StandardScaler()
            scaled_values = self.scalers['numerical_scaler'].fit_transform(df[numerical_features])
        else:
            scaled_values = self.scalers['numerical_scaler'].transform(df[numerical_features])
            
        for idx, feature in enumerate(numerical_features):
            df[f'{feature}_scaled'] = scaled_values[:, idx]
            
        return df
        
    def _add_derived_features(self, df: pd.DataFrame, db: Session) -> pd.DataFrame:
        """Add derived features"""
        # Convert transaction_date to datetime if not already
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Add temporal features
        df['year'] = df['transaction_date'].dt.year
        df['month'] = df['transaction_date'].dt.month
        df['day_of_week'] = df['transaction_date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Add category averages
        category_averages = df.groupby('category')['unit_price'].transform('mean')
        df['price_vs_category_avg'] = df['unit_price'] / category_averages
        
        # Add transaction counts per product
        df['transactions_per_product'] = df.groupby('product_id')['transaction_id'].transform('count')
        
        # Calculate moving averages
        df['price_7day_ma'] = df.groupby('product_id')['unit_price'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        
        return df
    
    def prepare_features_for_analysis(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> tuple:
        """Prepare features for analysis"""
        # Select features for analysis
        feature_columns = [
            'quantity_scaled', 'unit_price_scaled', 'total_value_scaled',
            'category_encoded', 'supplier_encoded', 'transaction_type_encoded',
            'year', 'month', 'day_of_week', 'is_weekend',
            'price_vs_category_avg', 'transactions_per_product'
        ]
        
        X = df[feature_columns]
        
        if target_column and target_column in df.columns:
            y = df[target_column]
            return X, y
        
        return X
    
    def transform_for_prediction(self, transaction: schemas.TransactionCreate) -> pd.DataFrame:
        """Transform a single transaction for prediction"""
        # Convert transaction to DataFrame
        df = pd.DataFrame([transaction.dict()])
        
        # Apply preprocessing steps
        df = self._handle_missing_values(df)
        df = self._encode_categorical_variables(df)
        df = self._scale_numerical_features(df)
        df = self._add_derived_features(df)
        
        return df
    
    def inverse_transform_predictions(
        self,
        predictions: np.ndarray,
        feature_name: str
    ) -> np.ndarray:
        """Inverse transform scaled predictions"""
        if f'numerical_scaler' in self.scalers:
            return self.scalers['numerical_scaler'].inverse_transform(predictions.reshape(-1, 1)).ravel()
        return predictions

# Create preprocessor instance
preprocessor = DataPreprocessor()