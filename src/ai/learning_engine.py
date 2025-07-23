#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Learning Engine for FionaSparx AI

This module implements machine learning capabilities for analyzing subscriber behavior,
content performance, and optimizing content generation strategies.

Key Features:
- Subscriber behavior analysis and learning
- Content performance prediction
- Optimal timing analysis
- Engagement pattern recognition
- Personalization engine
- A/B testing framework

Author: FionaSparx AI Content Creator
Version: 2.0.0
"""

import json
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import logging
import pickle
import os

logger = logging.getLogger(__name__)

@dataclass
class SubscriberProfile:
    """Subscriber behavior profile"""
    user_id: str
    platform: str
    engagement_score: float
    preferred_content_types: List[str]
    active_hours: List[int]
    interaction_patterns: Dict[str, float]
    spending_behavior: Dict[str, Any]
    lifetime_value: float
    churn_risk: float
    personalization_preferences: Dict[str, Any]
    last_updated: str

@dataclass
class ContentPerformance:
    """Content performance metrics"""
    content_id: str
    platform: str
    content_type: str
    posted_at: str
    engagement_metrics: Dict[str, float]
    quality_score: float
    reach: int
    conversion_rate: float
    revenue_generated: float
    optimal_timing_score: float

@dataclass
class LearningInsight:
    """AI learning insights"""
    insight_type: str
    confidence: float
    recommendation: str
    impact_prediction: float
    supporting_data: Dict[str, Any]
    created_at: str

class LearningEngine:
    """
    Advanced AI learning engine for subscriber behavior and content optimization
    """
    
    def __init__(self, database_path: str = "data/learning_engine.db"):
        """Initialize the learning engine"""
        self.database_path = database_path
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        
        # Model configurations
        self.model_configs = {
            'engagement_predictor': {
                'type': 'random_forest',
                'params': {'n_estimators': 100, 'random_state': 42}
            },
            'timing_optimizer': {
                'type': 'gradient_boosting',
                'params': {'n_estimators': 50, 'random_state': 42}
            },
            'subscriber_segmentation': {
                'type': 'kmeans',
                'params': {'n_clusters': 5, 'random_state': 42}
            },
            'content_recommender': {
                'type': 'random_forest',
                'params': {'n_estimators': 80, 'random_state': 42}
            }
        }
        
        self._initialize_database()
        self._load_models()
        
        logger.info("✅ Learning Engine initialized with AI models")
    
    def _initialize_database(self):
        """Initialize the learning database"""
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
        
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            # Subscriber profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriber_profiles (
                    user_id TEXT PRIMARY KEY,
                    platform TEXT,
                    engagement_score REAL,
                    preferred_content_types TEXT,
                    active_hours TEXT,
                    interaction_patterns TEXT,
                    spending_behavior TEXT,
                    lifetime_value REAL,
                    churn_risk REAL,
                    personalization_preferences TEXT,
                    last_updated TEXT
                )
            ''')
            
            # Content performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_performance (
                    content_id TEXT PRIMARY KEY,
                    platform TEXT,
                    content_type TEXT,
                    posted_at TEXT,
                    engagement_metrics TEXT,
                    quality_score REAL,
                    reach INTEGER,
                    conversion_rate REAL,
                    revenue_generated REAL,
                    optimal_timing_score REAL
                )
            ''')
            
            # Learning insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT,
                    confidence REAL,
                    recommendation TEXT,
                    impact_prediction REAL,
                    supporting_data TEXT,
                    created_at TEXT
                )
            ''')
            
            # Training data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_vector TEXT,
                    target_value REAL,
                    data_type TEXT,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            logger.info("📊 Learning database initialized")
    
    def _load_models(self):
        """Load pre-trained models if available"""
        model_dir = "data/models"
        os.makedirs(model_dir, exist_ok=True)
        
        for model_name in self.model_configs.keys():
            model_path = f"{model_dir}/{model_name}.pkl"
            scaler_path = f"{model_dir}/{model_name}_scaler.pkl"
            
            try:
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    logger.info(f"✅ Loaded pre-trained model: {model_name}")
                
                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scalers[model_name] = pickle.load(f)
                    logger.info(f"✅ Loaded scaler for: {model_name}")
                    
            except Exception as e:
                logger.warning(f"Could not load model {model_name}: {e}")
    
    def _save_models(self):
        """Save trained models"""
        model_dir = "data/models"
        os.makedirs(model_dir, exist_ok=True)
        
        for model_name, model in self.models.items():
            try:
                model_path = f"{model_dir}/{model_name}.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                
                if model_name in self.scalers:
                    scaler_path = f"{model_dir}/{model_name}_scaler.pkl"
                    with open(scaler_path, 'wb') as f:
                        pickle.dump(self.scalers[model_name], f)
                
                logger.info(f"💾 Saved model: {model_name}")
                
            except Exception as e:
                logger.error(f"Failed to save model {model_name}: {e}")
    
    def update_subscriber_profile(self, profile: SubscriberProfile):
        """Update or create subscriber profile"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO subscriber_profiles 
                (user_id, platform, engagement_score, preferred_content_types, active_hours,
                 interaction_patterns, spending_behavior, lifetime_value, churn_risk,
                 personalization_preferences, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile.user_id,
                profile.platform,
                profile.engagement_score,
                json.dumps(profile.preferred_content_types),
                json.dumps(profile.active_hours),
                json.dumps(profile.interaction_patterns),
                json.dumps(profile.spending_behavior),
                profile.lifetime_value,
                profile.churn_risk,
                json.dumps(profile.personalization_preferences),
                profile.last_updated
            ))
            
            conn.commit()
            logger.info(f"📝 Updated subscriber profile: {profile.user_id}")
    
    def record_content_performance(self, performance: ContentPerformance):
        """Record content performance metrics"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO content_performance 
                (content_id, platform, content_type, posted_at, engagement_metrics,
                 quality_score, reach, conversion_rate, revenue_generated, optimal_timing_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                performance.content_id,
                performance.platform,
                performance.content_type,
                performance.posted_at,
                json.dumps(performance.engagement_metrics),
                performance.quality_score,
                performance.reach,
                performance.conversion_rate,
                performance.revenue_generated,
                performance.optimal_timing_score
            ))
            
            conn.commit()
            logger.info(f"📊 Recorded content performance: {performance.content_id}")
    
    def analyze_subscriber_behavior(self, platform: str = None, days: int = 30) -> Dict[str, Any]:
        """Analyze subscriber behavior patterns"""
        with sqlite3.connect(self.database_path) as conn:
            query = '''
                SELECT * FROM subscriber_profiles 
                WHERE last_updated >= datetime('now', '-{} days')
            '''.format(days)
            
            if platform:
                query += f" AND platform = '{platform}'"
            
            df = pd.read_sql_query(query, conn)
        
        if df.empty:
            logger.warning("No subscriber data available for analysis")
            return {"error": "No data available"}
        
        # Parse JSON columns
        df['preferred_content_types'] = df['preferred_content_types'].apply(
            lambda x: json.loads(x) if x else []
        )
        df['active_hours'] = df['active_hours'].apply(
            lambda x: json.loads(x) if x else []
        )
        df['interaction_patterns'] = df['interaction_patterns'].apply(
            lambda x: json.loads(x) if x else {}
        )
        
        analysis = {
            'total_subscribers': len(df),
            'average_engagement': df['engagement_score'].mean(),
            'high_value_subscribers': len(df[df['lifetime_value'] > df['lifetime_value'].quantile(0.8)]),
            'churn_risk_analysis': {
                'high_risk': len(df[df['churn_risk'] > 0.7]),
                'medium_risk': len(df[(df['churn_risk'] > 0.3) & (df['churn_risk'] <= 0.7)]),
                'low_risk': len(df[df['churn_risk'] <= 0.3])
            },
            'content_preferences': {},
            'optimal_posting_hours': [],
            'engagement_patterns': {}
        }
        
        # Analyze content preferences
        all_content_types = []
        for types_list in df['preferred_content_types']:
            all_content_types.extend(types_list)
        
        content_type_counts = pd.Series(all_content_types).value_counts()
        analysis['content_preferences'] = content_type_counts.head(10).to_dict()
        
        # Analyze optimal posting hours
        all_hours = []
        for hours_list in df['active_hours']:
            all_hours.extend(hours_list)
        
        if all_hours:
            hour_counts = pd.Series(all_hours).value_counts()
            analysis['optimal_posting_hours'] = hour_counts.head(5).index.tolist()
        
        # Platform-specific insights
        if platform:
            platform_df = df[df['platform'] == platform]
            analysis['platform_specific'] = {
                'subscribers': len(platform_df),
                'avg_engagement': platform_df['engagement_score'].mean(),
                'avg_lifetime_value': platform_df['lifetime_value'].mean()
            }
        
        # Generate learning insights
        insights = self._generate_behavioral_insights(analysis)
        for insight in insights:
            self._store_insight(insight)
        
        logger.info(f"🧠 Analyzed behavior for {len(df)} subscribers")
        return analysis
    
    def predict_content_performance(self, content_features: Dict[str, Any]) -> Dict[str, float]:
        """Predict content performance using trained models"""
        if 'engagement_predictor' not in self.models:
            logger.warning("Engagement predictor model not trained")
            return self._fallback_prediction(content_features)
        
        try:
            # Extract features for prediction
            features = self._extract_content_features(content_features)
            features_array = np.array(features).reshape(1, -1)
            
            # Scale features if scaler is available
            if 'engagement_predictor' in self.scalers:
                features_array = self.scalers['engagement_predictor'].transform(features_array)
            
            # Predict engagement
            engagement_prediction = self.models['engagement_predictor'].predict(features_array)[0]
            
            # Predict optimal timing if model is available
            timing_score = 0.75  # Default
            if 'timing_optimizer' in self.models:
                timing_features = self._extract_timing_features(content_features)
                timing_array = np.array(timing_features).reshape(1, -1)
                
                if 'timing_optimizer' in self.scalers:
                    timing_array = self.scalers['timing_optimizer'].transform(timing_array)
                
                timing_score = self.models['timing_optimizer'].predict_proba(timing_array)[0][1]
            
            prediction = {
                'predicted_engagement': float(engagement_prediction),
                'timing_score': float(timing_score),
                'reach_estimate': int(engagement_prediction * 1000),  # Rough estimate
                'conversion_probability': float(engagement_prediction * 0.05),  # 5% conversion rate
                'confidence': 0.85 if self.is_trained else 0.60
            }
            
            logger.info(f"🎯 Predicted content performance: engagement={engagement_prediction:.2f}")
            return prediction
            
        except Exception as e:
            logger.error(f"Content performance prediction failed: {e}")
            return self._fallback_prediction(content_features)
    
    def get_optimal_posting_times(self, platform: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Analyze and recommend optimal posting times"""
        with sqlite3.connect(self.database_path) as conn:
            query = '''
                SELECT posted_at, engagement_metrics, reach, platform
                FROM content_performance 
                WHERE platform = ? AND posted_at >= datetime('now', '-{} days')
            '''.format(days_back)
            
            df = pd.read_sql_query(query, conn, params=(platform,))
        
        if df.empty:
            logger.warning(f"No content data for {platform} in last {days_back} days")
            return self._default_posting_times(platform)
        
        # Parse datetime and extract hour/day info
        df['posted_at'] = pd.to_datetime(df['posted_at'])
        df['hour'] = df['posted_at'].dt.hour
        df['day_of_week'] = df['posted_at'].dt.dayofweek
        
        # Parse engagement metrics
        df['engagement_metrics'] = df['engagement_metrics'].apply(
            lambda x: json.loads(x) if x else {}
        )
        df['total_engagement'] = df['engagement_metrics'].apply(
            lambda x: sum(x.values()) if isinstance(x, dict) else 0
        )
        
        # Calculate engagement rate
        df['engagement_rate'] = df['total_engagement'] / (df['reach'] + 1)  # Avoid division by zero
        
        # Analyze by hour
        hourly_performance = df.groupby('hour').agg({
            'engagement_rate': ['mean', 'std', 'count'],
            'reach': 'mean'
        }).round(4)
        
        # Analyze by day of week
        daily_performance = df.groupby('day_of_week').agg({
            'engagement_rate': ['mean', 'std', 'count'],
            'reach': 'mean'
        }).round(4)
        
        # Generate recommendations
        top_hours = hourly_performance.sort_values(('engagement_rate', 'mean'), ascending=False).head(5)
        top_days = daily_performance.sort_values(('engagement_rate', 'mean'), ascending=False).head(3)
        
        optimal_times = []
        
        for hour in top_hours.index:
            hour_data = hourly_performance.loc[hour]
            optimal_times.append({
                'hour': int(hour),
                'avg_engagement_rate': float(hour_data[('engagement_rate', 'mean')]),
                'avg_reach': float(hour_data[('reach', 'mean')]),
                'sample_size': int(hour_data[('engagement_rate', 'count')]),
                'confidence': min(0.95, hour_data[('engagement_rate', 'count')] / 10),  # More samples = higher confidence
                'recommendation': f"Post at {hour:02d}:00 for optimal engagement"
            })
        
        # Store insights
        insight = LearningInsight(
            insight_type="optimal_timing",
            confidence=0.8,
            recommendation=f"Best posting hours for {platform}: {[t['hour'] for t in optimal_times[:3]]}",
            impact_prediction=0.25,  # 25% improvement
            supporting_data={
                "platform": platform,
                "analysis_period_days": days_back,
                "sample_size": len(df),
                "top_hours": [t['hour'] for t in optimal_times[:3]]
            },
            created_at=datetime.now().isoformat()
        )
        self._store_insight(insight)
        
        logger.info(f"⏰ Analyzed optimal posting times for {platform}")
        return optimal_times
    
    def segment_subscribers(self, platform: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """Segment subscribers using machine learning clustering"""
        with sqlite3.connect(self.database_path) as conn:
            query = "SELECT * FROM subscriber_profiles"
            if platform:
                query += f" WHERE platform = '{platform}'"
            
            df = pd.read_sql_query(query, conn)
        
        if df.empty or len(df) < 10:  # Need minimum data for clustering
            logger.warning("Insufficient data for subscriber segmentation")
            return {"error": "Insufficient data for segmentation"}
        
        # Prepare features for clustering
        features = []
        for _, row in df.iterrows():
            interaction_patterns = json.loads(row['interaction_patterns']) if row['interaction_patterns'] else {}
            
            feature_vector = [
                row['engagement_score'],
                row['lifetime_value'],
                row['churn_risk'],
                interaction_patterns.get('likes_ratio', 0),
                interaction_patterns.get('comments_ratio', 0),
                interaction_patterns.get('shares_ratio', 0),
                interaction_patterns.get('tips_frequency', 0),
                len(json.loads(row['active_hours']) if row['active_hours'] else [])
            ]
            features.append(feature_vector)
        
        features_array = np.array(features)
        
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features_array)
        
        # Perform clustering
        n_clusters = min(5, len(df) // 2)  # Adjust clusters based on data size
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        # Store models
        self.models['subscriber_segmentation'] = kmeans
        self.scalers['subscriber_segmentation'] = scaler
        
        # Analyze clusters
        df['cluster'] = cluster_labels
        segments = {}
        
        for cluster_id in range(n_clusters):
            cluster_df = df[df['cluster'] == cluster_id]
            
            segment_name = self._name_segment(cluster_df)
            
            segments[segment_name] = {
                'subscriber_count': len(cluster_df),
                'characteristics': {
                    'avg_engagement': float(cluster_df['engagement_score'].mean()),
                    'avg_lifetime_value': float(cluster_df['lifetime_value'].mean()),
                    'avg_churn_risk': float(cluster_df['churn_risk'].mean())
                },
                'recommended_strategy': self._recommend_segment_strategy(cluster_df),
                'top_subscribers': cluster_df.nlargest(3, 'lifetime_value')[['user_id', 'engagement_score', 'lifetime_value']].to_dict('records')
            }
        
        # Store segmentation insights
        insight = LearningInsight(
            insight_type="subscriber_segmentation",
            confidence=0.75,
            recommendation=f"Identified {len(segments)} distinct subscriber segments",
            impact_prediction=0.35,  # 35% improvement through targeted content
            supporting_data={
                "platform": platform,
                "total_subscribers": len(df),
                "segments": list(segments.keys()),
                "clustering_features": ["engagement", "lifetime_value", "churn_risk", "interaction_patterns"]
            },
            created_at=datetime.now().isoformat()
        )
        self._store_insight(insight)
        
        logger.info(f"👥 Segmented {len(df)} subscribers into {len(segments)} segments")
        return segments
    
    def train_models(self, retrain: bool = False):
        """Train or retrain all ML models"""
        if self.is_trained and not retrain:
            logger.info("Models already trained. Use retrain=True to force retraining")
            return
        
        logger.info("🎓 Starting model training...")
        
        # Train engagement predictor
        self._train_engagement_predictor()
        
        # Train timing optimizer
        self._train_timing_optimizer()
        
        # Train content recommender
        self._train_content_recommender()
        
        self.is_trained = True
        self._save_models()
        
        logger.info("✅ Model training completed")
    
    def _train_engagement_predictor(self):
        """Train engagement prediction model"""
        with sqlite3.connect(self.database_path) as conn:
            df = pd.read_sql_query('''
                SELECT * FROM content_performance 
                WHERE posted_at >= datetime('now', '-90 days')
            ''', conn)
        
        if df.empty or len(df) < 20:
            logger.warning("Insufficient data for engagement predictor training")
            return
        
        # Extract features and targets
        X = []
        y = []
        
        for _, row in df.iterrows():
            features = self._extract_content_features({
                'platform': row['platform'],
                'content_type': row['content_type'],
                'quality_score': row['quality_score'],
                'hour': pd.to_datetime(row['posted_at']).hour,
                'day_of_week': pd.to_datetime(row['posted_at']).dayofweek
            })
            
            engagement_metrics = json.loads(row['engagement_metrics'])
            engagement_score = sum(engagement_metrics.values()) / (row['reach'] + 1)
            
            X.append(features)
            y.append(engagement_score)
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(**self.model_configs['engagement_predictor']['params'])
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        
        # Store model and scaler
        self.models['engagement_predictor'] = model
        self.scalers['engagement_predictor'] = scaler
        
        logger.info(f"✅ Engagement predictor trained. MSE: {mse:.4f}")
    
    def _train_timing_optimizer(self):
        """Train optimal timing model"""
        with sqlite3.connect(self.database_path) as conn:
            df = pd.read_sql_query('''
                SELECT * FROM content_performance 
                WHERE posted_at >= datetime('now', '-90 days')
            ''', conn)
        
        if df.empty or len(df) < 20:
            logger.warning("Insufficient data for timing optimizer training")
            return
        
        # Calculate engagement rates and create binary targets (above/below median)
        df['engagement_metrics'] = df['engagement_metrics'].apply(lambda x: json.loads(x))
        df['total_engagement'] = df['engagement_metrics'].apply(lambda x: sum(x.values()))
        df['engagement_rate'] = df['total_engagement'] / (df['reach'] + 1)
        
        engagement_median = df['engagement_rate'].median()
        
        X = []
        y = []
        
        for _, row in df.iterrows():
            features = self._extract_timing_features({
                'hour': pd.to_datetime(row['posted_at']).hour,
                'day_of_week': pd.to_datetime(row['posted_at']).dayofweek,
                'platform': row['platform'],
                'content_type': row['content_type']
            })
            
            target = 1 if row['engagement_rate'] > engagement_median else 0
            
            X.append(features)
            y.append(target)
        
        X = np.array(X)
        y = np.array(y)
        
        # Split and scale
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train classifier
        model = GradientBoostingClassifier(**self.model_configs['timing_optimizer']['params'])
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Store model and scaler
        self.models['timing_optimizer'] = model
        self.scalers['timing_optimizer'] = scaler
        
        logger.info(f"✅ Timing optimizer trained. Accuracy: {accuracy:.4f}")
    
    def _train_content_recommender(self):
        """Train content recommendation model"""
        # Simplified content recommender based on subscriber preferences
        with sqlite3.connect(self.database_path) as conn:
            profiles_df = pd.read_sql_query("SELECT * FROM subscriber_profiles", conn)
            content_df = pd.read_sql_query("SELECT * FROM content_performance", conn)
        
        if profiles_df.empty or content_df.empty:
            logger.warning("Insufficient data for content recommender training")
            return
        
        # This is a simplified implementation
        # In a full system, this would use collaborative filtering or matrix factorization
        
        content_performance = {}
        for _, row in content_df.iterrows():
            content_type = row['content_type']
            platform = row['platform']
            
            engagement_metrics = json.loads(row['engagement_metrics'])
            performance_score = sum(engagement_metrics.values()) / (row['reach'] + 1)
            
            key = f"{platform}_{content_type}"
            if key not in content_performance:
                content_performance[key] = []
            content_performance[key].append(performance_score)
        
        # Calculate average performance for each content type per platform
        avg_performance = {}
        for key, scores in content_performance.items():
            avg_performance[key] = np.mean(scores)
        
        # Store as simple lookup table (in real implementation, use proper ML model)
        self.models['content_recommender'] = avg_performance
        
        logger.info("✅ Content recommender trained")
    
    def _extract_content_features(self, content_data: Dict[str, Any]) -> List[float]:
        """Extract numerical features from content data"""
        features = []
        
        # Platform encoding (one-hot style)
        platforms = ['fanvue', 'loyalfans', 'instagram', 'twitter', 'tiktok']
        for platform in platforms:
            features.append(1.0 if content_data.get('platform') == platform else 0.0)
        
        # Content type encoding
        content_types = ['lifestyle', 'fashion', 'fitness', 'motivation', 'behind_scenes', 'personal', 'teaser']
        for content_type in content_types:
            features.append(1.0 if content_data.get('content_type') == content_type else 0.0)
        
        # Temporal features
        features.append(content_data.get('hour', 12) / 24.0)  # Normalized hour
        features.append(content_data.get('day_of_week', 3) / 7.0)  # Normalized day
        
        # Quality score
        features.append(content_data.get('quality_score', 3.0) / 5.0)  # Normalized quality
        
        # Other features
        features.append(content_data.get('word_count', 100) / 500.0)  # Normalized word count
        features.append(content_data.get('hashtag_count', 10) / 30.0)  # Normalized hashtag count
        
        return features
    
    def _extract_timing_features(self, timing_data: Dict[str, Any]) -> List[float]:
        """Extract timing-related features"""
        features = []
        
        # Hour features (cyclical encoding)
        hour = timing_data.get('hour', 12)
        features.append(np.sin(2 * np.pi * hour / 24))
        features.append(np.cos(2 * np.pi * hour / 24))
        
        # Day of week features (cyclical encoding)
        day = timing_data.get('day_of_week', 3)
        features.append(np.sin(2 * np.pi * day / 7))
        features.append(np.cos(2 * np.pi * day / 7))
        
        # Platform encoding
        platforms = ['fanvue', 'loyalfans', 'instagram', 'twitter', 'tiktok']
        for platform in platforms:
            features.append(1.0 if timing_data.get('platform') == platform else 0.0)
        
        return features
    
    def _generate_behavioral_insights(self, analysis: Dict[str, Any]) -> List[LearningInsight]:
        """Generate insights from behavioral analysis"""
        insights = []
        
        # Engagement insight
        if analysis['average_engagement'] > 0.7:
            insights.append(LearningInsight(
                insight_type="high_engagement",
                confidence=0.85,
                recommendation="Subscriber engagement is excellent. Maintain current content strategy.",
                impact_prediction=0.0,  # No change needed
                supporting_data={"avg_engagement": analysis['average_engagement']},
                created_at=datetime.now().isoformat()
            ))
        elif analysis['average_engagement'] < 0.3:
            insights.append(LearningInsight(
                insight_type="low_engagement",
                confidence=0.80,
                recommendation="Low engagement detected. Consider diversifying content types and posting times.",
                impact_prediction=0.40,  # Potential 40% improvement
                supporting_data={"avg_engagement": analysis['average_engagement']},
                created_at=datetime.now().isoformat()
            ))
        
        # Churn risk insight
        high_risk_ratio = analysis['churn_risk_analysis']['high_risk'] / analysis['total_subscribers']
        if high_risk_ratio > 0.3:
            insights.append(LearningInsight(
                insight_type="high_churn_risk",
                confidence=0.75,
                recommendation="High churn risk detected. Implement retention campaigns and personalized content.",
                impact_prediction=0.50,  # Potential 50% churn reduction
                supporting_data={"high_risk_ratio": high_risk_ratio},
                created_at=datetime.now().isoformat()
            ))
        
        # Content preference insight
        if analysis['content_preferences']:
            top_content = list(analysis['content_preferences'].keys())[0]
            insights.append(LearningInsight(
                insight_type="content_preference",
                confidence=0.70,
                recommendation=f"'{top_content}' content is most popular. Increase frequency of this content type.",
                impact_prediction=0.25,  # 25% engagement boost
                supporting_data={"top_content_type": top_content, "preferences": analysis['content_preferences']},
                created_at=datetime.now().isoformat()
            ))
        
        return insights
    
    def _store_insight(self, insight: LearningInsight):
        """Store learning insight in database"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO learning_insights 
                (insight_type, confidence, recommendation, impact_prediction, supporting_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                insight.insight_type,
                insight.confidence,
                insight.recommendation,
                insight.impact_prediction,
                json.dumps(insight.supporting_data),
                insight.created_at
            ))
            conn.commit()
    
    def _name_segment(self, segment_df: pd.DataFrame) -> str:
        """Generate descriptive name for subscriber segment"""
        avg_engagement = segment_df['engagement_score'].mean()
        avg_ltv = segment_df['lifetime_value'].mean()
        avg_churn = segment_df['churn_risk'].mean()
        
        if avg_engagement > 0.7 and avg_ltv > 100:
            return "VIP Enthusiasts"
        elif avg_engagement > 0.5 and avg_churn < 0.3:
            return "Loyal Supporters"
        elif avg_churn > 0.7:
            return "At-Risk Subscribers"
        elif avg_engagement < 0.3:
            return "Passive Viewers"
        else:
            return "Regular Subscribers"
    
    def _recommend_segment_strategy(self, segment_df: pd.DataFrame) -> str:
        """Recommend strategy for subscriber segment"""
        avg_engagement = segment_df['engagement_score'].mean()
        avg_churn = segment_df['churn_risk'].mean()
        
        if avg_engagement > 0.7:
            return "Maintain high-quality content, offer exclusive access"
        elif avg_churn > 0.7:
            return "Implement retention campaigns, personalized outreach"
        elif avg_engagement < 0.3:
            return "Create engaging content, increase interaction frequency"
        else:
            return "Gradual engagement building, diversified content strategy"
    
    def _fallback_prediction(self, content_features: Dict[str, Any]) -> Dict[str, float]:
        """Fallback prediction when models are not available"""
        # Simple heuristic-based prediction
        base_engagement = 0.5
        
        # Platform adjustments
        platform_multipliers = {
            'fanvue': 1.2,
            'loyalfans': 1.1,
            'instagram': 0.8,
            'twitter': 0.6,
            'tiktok': 1.0
        }
        
        platform = content_features.get('platform', 'fanvue')
        engagement = base_engagement * platform_multipliers.get(platform, 1.0)
        
        # Quality adjustment
        quality = content_features.get('quality_score', 3.0)
        engagement *= (quality / 3.0)
        
        return {
            'predicted_engagement': engagement,
            'timing_score': 0.75,
            'reach_estimate': int(engagement * 1000),
            'conversion_probability': engagement * 0.05,
            'confidence': 0.50  # Lower confidence for fallback
        }
    
    def _default_posting_times(self, platform: str) -> List[Dict[str, Any]]:
        """Default posting times when no data is available"""
        default_times = {
            'fanvue': [8, 12, 17, 20],
            'loyalfans': [9, 13, 18, 21],
            'instagram': [9, 12, 15, 19],
            'twitter': [8, 11, 14, 17],
            'tiktok': [10, 14, 18, 22]
        }
        
        hours = default_times.get(platform, [8, 12, 17, 20])
        
        return [{
            'hour': hour,
            'avg_engagement_rate': 0.5,
            'avg_reach': 1000,
            'sample_size': 0,
            'confidence': 0.3,
            'recommendation': f"Default recommendation: Post at {hour:02d}:00"
        } for hour in hours]
    
    def get_learning_insights(self, days_back: int = 7, insight_type: str = None) -> List[Dict[str, Any]]:
        """Get recent learning insights"""
        with sqlite3.connect(self.database_path) as conn:
            query = '''
                SELECT * FROM learning_insights 
                WHERE created_at >= datetime('now', '-{} days')
            '''.format(days_back)
            
            if insight_type:
                query += f" AND insight_type = '{insight_type}'"
            
            query += " ORDER BY created_at DESC LIMIT 20"
            
            cursor = conn.cursor()
            cursor.execute(query)
            
            insights = []
            for row in cursor.fetchall():
                insight = {
                    'id': row[0],
                    'insight_type': row[1],
                    'confidence': row[2],
                    'recommendation': row[3],
                    'impact_prediction': row[4],
                    'supporting_data': json.loads(row[5]) if row[5] else {},
                    'created_at': row[6]
                }
                insights.append(insight)
        
        logger.info(f"📋 Retrieved {len(insights)} learning insights")
        return insights
    
    def generate_content_strategy(self, platform: str, target_metrics: Dict[str, float] = None) -> Dict[str, Any]:
        """Generate AI-powered content strategy"""
        # Analyze recent performance
        behavior_analysis = self.analyze_subscriber_behavior(platform, days=30)
        optimal_times = self.get_optimal_posting_times(platform, days_back=30)
        recent_insights = self.get_learning_insights(days_back=14)
        
        # Default target metrics
        if not target_metrics:
            target_metrics = {
                'engagement_rate': 0.6,
                'reach_increase': 0.2,
                'conversion_rate': 0.05
            }
        
        strategy = {
            'platform': platform,
            'generated_at': datetime.now().isoformat(),
            'target_metrics': target_metrics,
            'recommendations': {
                'content_types': [],
                'posting_schedule': [],
                'engagement_tactics': [],
                'personalization': []
            },
            'predicted_outcomes': {},
            'confidence_score': 0.0
        }
        
        # Content type recommendations based on preferences
        if not behavior_analysis.get('error') and behavior_analysis.get('content_preferences'):
            top_content_types = list(behavior_analysis['content_preferences'].keys())[:3]
            strategy['recommendations']['content_types'] = [
                f"Focus on {content_type} content (high subscriber preference)" 
                for content_type in top_content_types
            ]
        
        # Posting schedule recommendations
        if optimal_times:
            top_hours = [t['hour'] for t in optimal_times[:3]]
            strategy['recommendations']['posting_schedule'] = [
                f"Post at {hour:02d}:00 for optimal engagement" 
                for hour in top_hours
            ]
        
        # Engagement tactics based on insights
        engagement_tactics = [
            "Include interactive questions to boost comment engagement",
            "Use optimal hashtag count (10-15 for this platform)",
            "Add call-to-action to encourage subscriber interaction",
            "Share behind-the-scenes content for authenticity"
        ]
        
        # Add insight-based tactics
        for insight in recent_insights:
            if insight['insight_type'] == 'low_engagement':
                engagement_tactics.append("Diversify content types to re-engage audience")
            elif insight['insight_type'] == 'high_churn_risk':
                engagement_tactics.append("Implement retention-focused content strategy")
        
        strategy['recommendations']['engagement_tactics'] = engagement_tactics[:5]
        
        # Personalization recommendations
        strategy['recommendations']['personalization'] = [
            "Segment content based on subscriber engagement levels",
            "Create VIP content for high-value subscribers",
            "Use behavioral data to optimize content timing",
            "Implement A/B testing for content variations"
        ]
        
        # Predict outcomes using models
        sample_content = {
            'platform': platform,
            'content_type': 'lifestyle',
            'quality_score': 4.0,
            'hour': optimal_times[0]['hour'] if optimal_times else 12,
            'day_of_week': 3
        }
        
        prediction = self.predict_content_performance(sample_content)
        strategy['predicted_outcomes'] = {
            'engagement_improvement': f"+{prediction.get('predicted_engagement', 0.5) * 100:.1f}%",
            'reach_estimate': prediction.get('reach_estimate', 1000),
            'conversion_probability': f"{prediction.get('conversion_probability', 0.05) * 100:.1f}%"
        }
        
        # Calculate confidence score
        factors = [
            len(behavior_analysis.get('content_preferences', {})) > 0,  # Has preference data
            len(optimal_times) > 0,  # Has timing data
            len(recent_insights) > 0,  # Has recent insights
            self.is_trained,  # Models are trained
            prediction.get('confidence', 0.5) > 0.7  # High prediction confidence
        ]
        
        strategy['confidence_score'] = sum(factors) / len(factors)
        
        logger.info(f"🎯 Generated content strategy for {platform} (confidence: {strategy['confidence_score']:.2f})")
        return strategy

# Example usage and testing
if __name__ == "__main__":
    # Initialize learning engine
    engine = LearningEngine()
    
    # Example subscriber profile
    profile = SubscriberProfile(
        user_id="user_123",
        platform="fanvue",
        engagement_score=0.75,
        preferred_content_types=["lifestyle", "fashion"],
        active_hours=[8, 12, 17, 20],
        interaction_patterns={"likes_ratio": 0.8, "comments_ratio": 0.6, "tips_frequency": 0.3},
        spending_behavior={"monthly_average": 50.0, "tip_frequency": "weekly"},
        lifetime_value=300.0,
        churn_risk=0.2,
        personalization_preferences={"content_style": "authentic", "interaction_level": "high"},
        last_updated=datetime.now().isoformat()
    )
    
    # Update profile
    engine.update_subscriber_profile(profile)
    
    # Example content performance
    performance = ContentPerformance(
        content_id="content_456",
        platform="fanvue",
        content_type="lifestyle",
        posted_at=datetime.now().isoformat(),
        engagement_metrics={"likes": 45, "comments": 12, "shares": 3},
        quality_score=4.2,
        reach=1000,
        conversion_rate=0.06,
        revenue_generated=30.0,
        optimal_timing_score=0.85
    )
    
    # Record performance
    engine.record_content_performance(performance)
    
    # Analyze behavior
    analysis = engine.analyze_subscriber_behavior("fanvue")
    print("Behavior Analysis:", json.dumps(analysis, indent=2))
    
    # Get optimal times
    optimal_times = engine.get_optimal_posting_times("fanvue")
    print("Optimal Times:", json.dumps(optimal_times, indent=2))
    
    # Generate strategy
    strategy = engine.generate_content_strategy("fanvue")
    print("Content Strategy:", json.dumps(strategy, indent=2))
    
    print("✅ Learning Engine test completed")