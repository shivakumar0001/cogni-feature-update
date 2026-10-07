"""
Feature Metrics API Endpoints
Provides access to feature performance metrics, accuracy, F1 scores
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.feature_monitor import FeatureMonitor
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/feature-metrics", tags=["feature-metrics"])


# Pydantic schemas
class FeatureMetricResponse(BaseModel):
    """Response model for feature metrics"""
    id: int
    feature_name: str
    feature_category: str
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    success_rate: Optional[float] = None
    error_rate: Optional[float] = None
    avg_response_time: Optional[float] = None
    total_requests: int
    successful_requests: int
    failed_requests: int
    is_active: bool
    health_status: str
    last_tested: Optional[str] = None
    last_updated: Optional[str] = None
    metadata: Optional[dict] = None


class SystemHealthResponse(BaseModel):
    """System health summary"""
    overall_health: str
    total_features: int
    healthy_features: int
    degraded_features: int
    critical_features: int
    avg_accuracy: Optional[float] = None
    avg_f1_score: Optional[float] = None
    avg_success_rate: Optional[float] = None
    total_requests: int
    successful_requests: int
    failed_requests: int


class FeatureTestResponse(BaseModel):
    """Feature test result"""
    id: int
    feature_name: str
    test_type: str
    test_passed: bool
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    tested_at: Optional[str] = None


class RecordTestRequest(BaseModel):
    """Request to record a test result"""
    feature_name: str = Field(..., description="Name of the feature")
    test_type: str = Field(..., description="Type of test: unit, integration, performance")
    test_passed: bool = Field(..., description="Whether the test passed")
    accuracy: Optional[float] = Field(None, ge=0, le=1, description="Accuracy (0-1)")
    f1_score: Optional[float] = Field(None, ge=0, le=1, description="F1 Score (0-1)")
    precision: Optional[float] = Field(None, ge=0, le=1, description="Precision (0-1)")
    recall: Optional[float] = Field(None, ge=0, le=1, description="Recall (0-1)")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    test_input: Optional[str] = Field(None, description="Test input data")
    test_output: Optional[str] = Field(None, description="Test output")
    expected_output: Optional[str] = Field(None, description="Expected output")
    error_message: Optional[str] = Field(None, description="Error message if failed")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[FeatureMetricResponse])
async def get_all_feature_metrics(
    category: Optional[str] = Query(None, description="Filter by category: ML, AI, Analytics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get performance metrics for all features
    
    Returns accuracy, F1 score, precision, recall, and other metrics for each feature
    """
    monitor = FeatureMonitor(db)
    
    if category:
        metrics = monitor.get_metrics_by_category(category)
    else:
        metrics = monitor.get_all_metrics()
    
    return metrics


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall system health summary
    
    Includes:
    - Overall health status (healthy, degraded, critical)
    - Number of features in each status
    - Average accuracy, F1 score, success rate across all features
    - Total requests and success/failure counts
    """
    monitor = FeatureMonitor(db)
    health = monitor.get_system_health()
    return health


@router.get("/{feature_name}", response_model=FeatureMetricResponse)
async def get_feature_metrics(
    feature_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get performance metrics for a specific feature
    
    Returns detailed metrics including:
    - Accuracy (percentage)
    - F1 Score (percentage)
    - Precision (percentage)
    - Recall (percentage)
    - Success rate
    - Error rate
    - Average response time
    - Request counts
    - Health status
    """
    monitor = FeatureMonitor(db)
    metrics = monitor.get_feature_metrics(feature_name)
    
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Feature '{feature_name}' not found")
    
    return metrics


@router.get("/tests/recent", response_model=List[FeatureTestResponse])
async def get_recent_tests(
    feature_name: Optional[str] = Query(None, description="Filter by feature name"),
    limit: int = Query(10, ge=1, le=100, description="Number of tests to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent test results
    
    Shows the most recent test executions with their results, metrics, and any errors
    """
    monitor = FeatureMonitor(db)
    tests = monitor.get_recent_tests(feature_name=feature_name, limit=limit)
    return tests


@router.post("/tests/record")
async def record_test_result(
    test_data: RecordTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a feature test result
    
    Use this to manually record test results including:
    - Test type (unit, integration, performance)
    - Pass/fail status
    - Accuracy, F1 score, precision, recall
    - Execution time
    - Error messages
    
    This will automatically update the feature's overall metrics
    """
    monitor = FeatureMonitor(db)
    
    monitor.record_test(
        feature_name=test_data.feature_name,
        test_type=test_data.test_type,
        test_passed=test_data.test_passed,
        accuracy=test_data.accuracy,
        f1_score=test_data.f1_score,
        precision=test_data.precision,
        recall=test_data.recall,
        execution_time=test_data.execution_time,
        test_input=test_data.test_input,
        test_output=test_data.test_output,
        expected_output=test_data.expected_output,
        error_message=test_data.error_message
    )
    
    return {
        "success": True,
        "message": f"Test result recorded for {test_data.feature_name}",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/{feature_name}/reset")
async def reset_feature_metrics(
    feature_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reset metrics for a specific feature
    
    This will:
    - Clear all request counts
    - Reset accuracy, F1 score, and other metrics to null
    - Clear error details
    - Set health status to healthy
    
    Use this when you want to start fresh tracking for a feature
    """
    # Only admins can reset metrics
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    monitor = FeatureMonitor(db)
    monitor.reset_feature_metrics(feature_name)
    
    return {
        "success": True,
        "message": f"Metrics reset for {feature_name}",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/categories/list")
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all feature categories
    
    Returns: ML, AI, Analytics
    """
    return {
        "categories": ["ML", "AI", "Analytics"],
        "features": FeatureMonitor.FEATURES
    }


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard data
    
    Includes:
    - System health
    - All feature metrics grouped by category
    - Recent tests
    - Performance trends
    """
    monitor = FeatureMonitor(db)
    
    health = monitor.get_system_health()
    all_metrics = monitor.get_all_metrics()
    recent_tests = monitor.get_recent_tests(limit=20)
    
    # Group by category
    ml_features = [m for m in all_metrics if m["feature_category"] == "ML"]
    ai_features = [m for m in all_metrics if m["feature_category"] == "AI"]
    analytics_features = [m for m in all_metrics if m["feature_category"] == "Analytics"]
    
    return {
        "system_health": health,
        "metrics_by_category": {
            "ML": ml_features,
            "AI": ai_features,
            "Analytics": analytics_features
        },
        "recent_tests": recent_tests,
        "timestamp": datetime.utcnow().isoformat()
    }
