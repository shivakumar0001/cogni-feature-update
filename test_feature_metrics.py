"""
Test script to populate feature metrics with sample data
Run this to see metrics in the dashboard immediately
"""
import requests
import time

BASE_URL = "http://localhost:8000"

# Login credentials
LOGIN_DATA = {
    "email": "rudraadmin@gmail.com",
    "password": "adminrudra@1234"
}

def get_token():
    """Login and get JWT token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=LOGIN_DATA)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def record_test_metrics(token):
    """Record sample test metrics for features"""
    headers = {"Authorization": f"Bearer {token}"}
    
    test_cases = [
        {
            "feature_name": "AutoML Training",
            "test_type": "performance",
            "test_passed": True,
            "accuracy": 0.87,
            "f1_score": 0.85,
            "precision": 0.88,
            "recall": 0.82,
            "execution_time": 2.5
        },
        {
            "feature_name": "Model Prediction",
            "test_type": "integration",
            "test_passed": True,
            "accuracy": 0.89,
            "f1_score": 0.87,
            "precision": 0.91,
            "recall": 0.84,
            "execution_time": 0.3
        },
        {
            "feature_name": "AI Chat",
            "test_type": "unit",
            "test_passed": True,
            "execution_time": 1.2
        },
        {
            "feature_name": "SQL Agent",
            "test_type": "unit",
            "test_passed": True,
            "execution_time": 0.8
        },
        {
            "feature_name": "RAG System",
            "test_type": "integration",
            "test_passed": True,
            "execution_time": 1.5
        }
    ]
    
    print("\n📊 Recording test metrics...\n")
    
    for test in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/feature-metrics/tests/record",
                json=test,
                headers=headers
            )
            if response.status_code == 200:
                feature = test["feature_name"]
                if "accuracy" in test:
                    print(f"✅ {feature}: Accuracy={test['accuracy']*100:.1f}%, F1={test['f1_score']*100:.1f}%")
                else:
                    print(f"✅ {feature}: Test recorded")
            else:
                print(f"❌ Failed to record {test['feature_name']}: {response.text}")
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✨ Metrics recorded! Check the Feature Metrics dashboard now.")

def main():
    print("=" * 60)
    print("  Feature Metrics Test - Populate Sample Data")
    print("=" * 60)
    
    # Get authentication token
    print("\n🔐 Authenticating...")
    token = get_token()
    
    if not token:
        print("\n❌ Could not authenticate. Make sure the backend is running.")
        return
    
    print("✅ Authenticated successfully!")
    
    # Record test metrics
    record_test_metrics(token)
    
    print("\n" + "=" * 60)
    print("  🎯 Done! Now check the Feature Metrics page")
    print("=" * 60)
    print("\n📍 Go to: http://localhost:5173/metrics")
    print("\n")

if __name__ == "__main__":
    main()
