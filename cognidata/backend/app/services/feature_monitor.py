"""
Feature Performance Monitoring Service
Tracks and calculates accuracy, F1 scores, and other metrics for each feature
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import time
import traceback
import numpy as np

from app.models.feature_metrics import FeatureMetrics, FeatureTest


class FeatureMonitor:
    """Monitor and track feature performance metrics"""
    
    # Define all features to monitor
    FEATURES = {
        "AutoML Training": {
            "category": "ML",
            "description": "Automated machine learning model training",
            "endpoints": ["/api/ml/train", "/api/ml/automl"]
        },
        "Model Prediction": {
            "category": "ML",
            "description": "ML model predictions",
            "endpoints": ["/api/ml/predict"]
        },
        "AI Chat": {
            "category": "AI",
            "description": "Natural language AI assistant",
            "endpoints": ["/api/ai/chat", "/api/ai/stream"]
        },
        "SQL Agent": {
            "category": "AI",
            "description": "Natural language to SQL conversion",
            "endpoints": ["/api/sql/agent"]
        },
        "RAG System": {
            "category": "AI",
            "description": "Document Q&A with retrieval",
            "endpoints": ["/api/rag/query"]
        },
        "Data Visualization": {
            "category": "Analytics",
            "description": "Chart and graph generation",
            "endpoints": ["/api/viz/overview", "/api/viz/create"]
        },
        "Data Profiling": {
            "category": "Analytics",
            "description": "Dataset analysis and statistics",
            "endpoints": ["/api/analytics/profile"]
        },
        "Deep Analyst": {
            "category": "AI",
            "description": "Multi-step reasoning analysis",
            "endpoints": ["/api/analyst/deep"]
        },
        "Geospatial Analysis": {
            "category": "Analytics",
            "description": "Map and location-based analysis",
            "endpoints": ["/api/geo/analyze"]
        },
        "Report Generation": {
            "category": "Analytics",
            "description": "PDF report creation",
            "endpoints": ["/api/reports/generate"]
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
        self._initialize_features()
    
    def _initialize_features(self):
        """Initialize all features in database if not exists"""
        for feature_name, info in self.FEATURES.items():
            existing = self.db.query(FeatureMetrics).filter(
                FeatureMetrics.feature_name == feature_name
            ).first()
            
            if not existing:
                metric = FeatureMetrics(
                    feature_name=feature_name,
                    feature_category=info["category"],
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    is_active=True,
                    health_status="healthy",
                    metadata={"description": info["description"], "endpoints": info["endpoints"]}
                )
                self.db.add(metric)
        
        self.db.commit()
    
    def track_request(
        self, 
        feature_name: str, 
        success: bool, 
        response_time: float,
        accuracy: Optional[float] = None,
        f1_score: Optional[float] = None,
        precision: Optional[float] = None,
        recall: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """Track a feature request and update metrics"""
        metric = self.db.query(FeatureMetrics).filter(
            FeatureMetrics.feature_name == feature_name
        ).first()
        
        if not metric:
            return
        
        # Update request counts
        metric.total_requests += 1
        if success:
            metric.successful_requests += 1
        else:
            metric.failed_requests += 1
        
        # Calculate success rate and error rate
        metric.success_rate = metric.successful_requests / metric.total_requests if metric.total_requests > 0 else 0
        metric.error_rate = metric.failed_requests / metric.total_requests if metric.total_requests > 0 else 0
        
        # Update average response time (exponential moving average)
        if metric.avg_response_time is None:
            metric.avg_response_time = response_time
        else:
            # 80% old, 20% new
            metric.avg_response_time = 0.8 * metric.avg_response_time + 0.2 * response_time
        
        # Update accuracy metrics if provided
        if accuracy is not None:
            if metric.accuracy is None:
                metric.accuracy = accuracy
            else:
                metric.accuracy = 0.7 * metric.accuracy + 0.3 * accuracy
        
        if f1_score is not None:
            if metric.f1_score is None:
                metric.f1_score = f1_score
            else:
                metric.f1_score = 0.7 * metric.f1_score + 0.3 * f1_score
        
        if precision is not None:
            if metric.precision is None:
                metric.precision = precision
            else:
                metric.precision = 0.7 * metric.precision + 0.3 * precision
        
        if recall is not None:
            if metric.recall is None:
                metric.recall = recall
            else:
                metric.recall = 0.7 * metric.recall + 0.3 * recall
        
        # Update health status
        if not success and error_message:
            metric.error_details = error_message[:500]  # Store last error
        
        metric.health_status = self._calculate_health_status(metric)
        metric.last_tested = datetime.utcnow()
        
        self.db.commit()
    
    def _calculate_health_status(self, metric: FeatureMetrics) -> str:
        """Calculate health status based on metrics"""
        # Critical if error rate > 30% or success rate < 50%
        if metric.error_rate and metric.error_rate > 0.3:
            return "critical"
        if metric.success_rate and metric.success_rate < 0.5:
            return "critical"
        
        # Degraded if error rate > 10% or success rate < 80%
        if metric.error_rate and metric.error_rate > 0.1:
            return "degraded"
        if metric.success_rate and metric.success_rate < 0.8:
            return "degraded"
        
        # Degraded if accuracy < 70% (for ML features)
        if metric.accuracy and metric.accuracy < 0.7:
            return "degraded"
        
        return "healthy"
    
    def get_all_metrics(self) -> List[Dict]:
        """Get all feature metrics"""
        metrics = self.db.query(FeatureMetrics).all()
        return [m.to_dict() for m in metrics]
    
    def get_feature_metrics(self, feature_name: str) -> Optional[Dict]:
        """Get metrics for a specific feature"""
        metric = self.db.query(FeatureMetrics).filter(
            FeatureMetrics.feature_name == feature_name
        ).first()
        return metric.to_dict() if metric else None
    
    def get_metrics_by_category(self, category: str) -> List[Dict]:
        """Get all metrics for a category"""
        metrics = self.db.query(FeatureMetrics).filter(
            FeatureMetrics.feature_category == category
        ).all()
        return [m.to_dict() for m in metrics]
    
    def get_system_health(self) -> Dict:
        """Get overall system health summary"""
        metrics = self.db.query(FeatureMetrics).all()
        
        if not metrics:
            return {
                "overall_health": "unknown",
                "total_features": 0,
                "healthy_features": 0,
                "degraded_features": 0,
                "critical_features": 0,
                "avg_accuracy": None,
                "avg_f1_score": None,
                "avg_success_rate": None
            }
        
        healthy = sum(1 for m in metrics if m.health_status == "healthy")
        degraded = sum(1 for m in metrics if m.health_status == "degraded")
        critical = sum(1 for m in metrics if m.health_status == "critical")
        
        # Calculate averages
        accuracies = [m.accuracy for m in metrics if m.accuracy is not None]
        f1_scores = [m.f1_score for m in metrics if m.f1_score is not None]
        success_rates = [m.success_rate for m in metrics if m.success_rate is not None]
        
        avg_accuracy = np.mean(accuracies) if accuracies else None
        avg_f1 = np.mean(f1_scores) if f1_scores else None
        avg_success = np.mean(success_rates) if success_rates else None
        
        # Determine overall health
        if critical > 0:
            overall_health = "critical"
        elif degraded > len(metrics) * 0.3:  # More than 30% degraded
            overall_health = "degraded"
        else:
            overall_health = "healthy"
        
        return {
            "overall_health": overall_health,
            "total_features": len(metrics),
            "healthy_features": healthy,
            "degraded_features": degraded,
            "critical_features": critical,
            "avg_accuracy": round(avg_accuracy * 100, 2) if avg_accuracy else None,
            "avg_f1_score": round(avg_f1 * 100, 2) if avg_f1 else None,
            "avg_success_rate": round(avg_success * 100, 2) if avg_success else None,
            "total_requests": sum(m.total_requests for m in metrics),
            "successful_requests": sum(m.successful_requests for m in metrics),
            "failed_requests": sum(m.failed_requests for m in metrics)
        }
    
    def record_test(
        self,
        feature_name: str,
        test_type: str,
        test_passed: bool,
        accuracy: Optional[float] = None,
        f1_score: Optional[float] = None,
        precision: Optional[float] = None,
        recall: Optional[float] = None,
        execution_time: Optional[float] = None,
        test_input: Optional[str] = None,
        test_output: Optional[str] = None,
        expected_output: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Record a feature test result"""
        test = FeatureTest(
            feature_name=feature_name,
            test_type=test_type,
            test_passed=test_passed,
            accuracy=accuracy,
            f1_score=f1_score,
            precision=precision,
            recall=recall,
            execution_time=execution_time,
            test_input=test_input[:1000] if test_input else None,
            test_output=test_output[:1000] if test_output else None,
            expected_output=expected_output[:1000] if expected_output else None,
            error_message=error_message[:500] if error_message else None
        )
        self.db.add(test)
        self.db.commit()
        
        # Update main metrics based on test
        self.track_request(
            feature_name=feature_name,
            success=test_passed,
            response_time=execution_time or 0,
            accuracy=accuracy,
            f1_score=f1_score,
            precision=precision,
            recall=recall,
            error_message=error_message
        )
    
    def get_recent_tests(self, feature_name: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent test results"""
        query = self.db.query(FeatureTest)
        
        if feature_name:
            query = query.filter(FeatureTest.feature_name == feature_name)
        
        tests = query.order_by(desc(FeatureTest.tested_at)).limit(limit).all()
        
        return [{
            "id": t.id,
            "feature_name": t.feature_name,
            "test_type": t.test_type,
            "test_passed": t.test_passed,
            "accuracy": round(t.accuracy * 100, 2) if t.accuracy else None,
            "f1_score": round(t.f1_score * 100, 2) if t.f1_score else None,
            "precision": round(t.precision * 100, 2) if t.precision else None,
            "recall": round(t.recall * 100, 2) if t.recall else None,
            "execution_time": round(t.execution_time, 3) if t.execution_time else None,
            "error_message": t.error_message,
            "tested_at": t.tested_at.isoformat() if t.tested_at else None
        } for t in tests]
    
    def reset_feature_metrics(self, feature_name: str):
        """Reset metrics for a specific feature"""
        metric = self.db.query(FeatureMetrics).filter(
            FeatureMetrics.feature_name == feature_name
        ).first()
        
        if metric:
            metric.total_requests = 0
            metric.successful_requests = 0
            metric.failed_requests = 0
            metric.success_rate = 0
            metric.error_rate = 0
            metric.accuracy = None
            metric.f1_score = None
            metric.precision = None
            metric.recall = None
            metric.avg_response_time = None
            metric.error_details = None
            metric.health_status = "healthy"
            self.db.commit()


# Helper function for ML model evaluation
def calculate_ml_metrics(y_true: List, y_pred: List) -> Dict[str, float]:
    """Calculate accuracy, F1, precision, recall for ML predictions"""
    try:
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        
        # Handle binary and multiclass
        is_binary = len(set(y_true)) == 2
        average = 'binary' if is_binary else 'weighted'
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average=average, zero_division=0),
            'recall': recall_score(y_true, y_pred, average=average, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, average=average, zero_division=0)
        }
        
        return metrics
    except Exception as e:
        print(f"Error calculating ML metrics: {e}")
        return {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0
        }
