"""Geo Intelligence routes - live city data, history, pipeline."""
import sys, pathlib, time
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user, get_db
from app.services.feature_monitor import FeatureMonitor
from sqlalchemy.orm import Session

router = APIRouter(prefix="/geo", tags=["Geo Intelligence"])

def _boot():
    p = str(pathlib.Path(__file__).resolve().parents[3] / "services")
    if p not in sys.path: sys.path.insert(0, p)

@router.get("/current")
def current(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    start_time = time.time()
    monitor = FeatureMonitor(db)
    
    try:
        _boot()
        from agents.geo.geo_agent import get_current
        data = get_current()
        
        # Track successful geospatial request
        monitor.track_request(
            "Geospatial Analysis",
            success=True,
            response_time=time.time() - start_time,
            metadata={"cities_count": len(data)}
        )
        
        return {"cities": list(data.values())}
    except Exception as e:
        monitor.track_request("Geospatial Analysis", success=False, response_time=time.time() - start_time)
        raise

@router.get("/history/{city}")
def city_history(city: str, n: int = 60, _: dict = Depends(get_current_user)):
    _boot()
    from agents.geo.geo_agent import get_history
    return {"city": city, "history": get_history(city, n)}

@router.get("/history")
def all_history(n: int = 60, _: dict = Depends(get_current_user)):
    _boot()
    from agents.geo.geo_agent import get_all_history
    return get_all_history(n)


@router.post("/sync")
def sync_real_data(data: dict, _: dict = Depends(get_current_user)):
    """Accept manually entered city data and inject into geo simulation."""
    cities = data.get("cities", [])
    if not cities:
        return {"message": "No cities provided"}
    try:
        _boot()
        from agents.geo.geo_agent import _current, _lock
        with _lock:
            for c in cities:
                name = c.get("name", "")
                if name:
                    _current[name] = {
                        "name": name,
                        "lat": float(c.get("lat", 0)),
                        "lon": float(c.get("lon", 0)),
                        "sales": float(c.get("sales", 0)),
                        "satisfaction": float(c.get("satisfaction", 4.0)),
                        "orders": int(c.get("orders", 100)),
                        "region": c.get("region", "Custom"),
                        "anomaly": False,
                        "tier": "Mid",
                    }
        return {"message": f"Synced {len(cities)} cities", "count": len(cities)}
    except Exception as e:
        return {"message": f"Sync failed: {e}", "count": 0}
