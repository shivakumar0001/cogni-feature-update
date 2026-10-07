"""
Feature Performance Metrics Model
Tracks accuracy, F1 score, precision, recall for each AI/ML feature
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from app.core.database import Base


class FeatureMetrics(Base):
    """Track performance metrics for each feature in the application"""
    __tablename__ = "feature_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Feature identification
    feature_name = Column(String(100), nullable=False, index=True)
    feature_category = Column(String(50), nullable=False)  # ML, AI, Analytics, etc.
    
    # Performance metrics
    accuracy = Column(Float, nullable=True)  # 0-1 scale
    f1_score = Column(Float, nullable=True)  # 0-1 scale
    precision = Column(Float, nullable=True)  # 0-1 scale
    recall = Column(Float, nullable=True)  # 0-1 scale
    
    # Additional metrics
    success_rate = Column(Float, nullable=True)  # Overall success rate
    error_rate = Column(Float, nullable=True)  # Error percentage
    avg_response_time = Column(Float, nullable=True)  # In seconds
    
    # Usage statistics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    health_status = Column(String(20), default="healthy")  # healthy, degraded, critical
    
    # Metadata
    last_tested = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional info (JSON for flexibility)
    metadata = Column(JSON, nullable=True)
    error_details = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<FeatureMetrics {self.feature_name}: Accuracy={self.accuracy}, F1={self.f1_score}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "feature_name": self.feature_name,
            "feature_category": self.feature_category,
            "accuracy": round(self.accuracy * 100, 2) if self.accuracy else None,
            "f1_score": round(self.f1_score * 100, 2) if self.f1_score else None,
            "precision": round(self.precision * 100, 2) if self.precision else None,
            "recall": round(self.recall * 100, 2) if self.recall else None,
            "success_rate": round(self.success_rate * 100, 2) if self.success_rate else None,
            "error_rate": round(self.error_rate * 100, 2) if self.error_rate else None,
            "avg_response_time": round(self.avg_response_time, 3) if self.avg_response_time else None,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "is_active": self.is_active,
            "health_status": self.health_status,
            "last_tested": self.last_tested.isoformat() if self.last_tested else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata,
            "error_details": self.error_details
        }


class FeatureTest(Base):
    """Store individual feature test results"""
    __tablename__ = "feature_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String(100), nullable=False, index=True)
    
    # Test results
    accuracy = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    
    # Test details
    test_type = Column(String(50), nullable=False)  # unit, integration, performance
    test_passed = Column(Boolean, default=False)
    execution_time = Column(Float, nullable=True)  # In seconds
    
    # Test data
    test_input = Column(Text, nullable=True)
    test_output = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    tested_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeatureTest {self.feature_name}: Passed={self.test_passed}>"
