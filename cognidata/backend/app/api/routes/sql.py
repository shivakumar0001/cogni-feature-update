"""SQL Agent routes - NL-pandas with auto-fix."""
import sys, pathlib, time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.deps import get_current_user, get_api_key, get_db
from app.services.data_store import get as get_df
from app.services.feature_monitor import FeatureMonitor
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sql", tags=["SQL Agent"])

def _boot():
    p = str(pathlib.Path(__file__).resolve().parents[3] / "services")
    if p not in sys.path: sys.path.insert(0, p)

class SQLQuery(BaseModel):
    question: str

@router.post("/query")
def sql_query(req: SQLQuery, api_key: str = Depends(get_api_key),
              user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    start_time = time.time()
    monitor = FeatureMonitor(db)
    
    try:
        _boot()
        from agents.sql.sql_agent import run_sql_agent
        df = get_df(user["email"])
        if df is None:
            monitor.track_request("SQL Agent", success=False, response_time=time.time() - start_time)
            raise HTTPException(404, "No dataset found")
        
        result = run_sql_agent(req.question, df, api_key)
        if result.get("error") and result.get("result") is None:
            monitor.track_request("SQL Agent", success=False, response_time=time.time() - start_time)
            raise HTTPException(422, result["error"])

        import pandas as pd
        r = result.get("result")
        if isinstance(r, pd.DataFrame):
            data = r.replace({float("nan"): None}).to_dict("records")
            rtype = "table"
        elif isinstance(r, pd.Series):
            data = r.where(r.notna(), None).to_dict()
            rtype = "json"
        else:
            data = str(r) if r is not None else None
            rtype = "text"

        # Track successful query
        monitor.track_request(
            "SQL Agent",
            success=True,
            response_time=time.time() - start_time,
            metadata={"question_length": len(req.question), "result_type": rtype}
        )

        return {"type": rtype, "data": data, "code": result.get("code"), "task_type": "sql"}
    except Exception as e:
        monitor.track_request("SQL Agent", success=False, response_time=time.time() - start_time)
        raise
