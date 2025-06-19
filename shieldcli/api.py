from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import jwt
from jwt import PyJWTError
import os
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Dict, Any
import uvicorn

app = FastAPI()
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET_KEY")

# Base SQLAlchemy
Base = declarative_base()

class ReportDB(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    agent_id = Column(String, index=True)
    timestamp = Column(DateTime)
    audit = Column(Text)  # stocké en JSON string
    integrity_alerts = Column(Text)  # stocké en JSON string

DATABASE_URL = "sqlite:///./reports.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

# Modèle de données
class Report(BaseModel):
    timestamp: str
    audit: Dict[str, Any]
    integrity_alerts: Any

@app.post("/login")
def login(data: Dict[str, str] = Body(...)):
    agent_id = data.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="agent_id required")
    payload = {
        "sub": agent_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token}

# Auth
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["sub"]
    except PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token or expired")

# @app.get("/compliance-audit")
# def get_audit_script(token_sub: str = Depends(verify_token)):
#     try:
#         with open("./compliance/compliance_audit.py", "r") as f:
#             return {"script": f.read()}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Script not found or error")

@app.post("/report")
def receive_report(report: Report, agent_id: str = Depends(verify_token)):
    db = SessionLocal()
    report_db = ReportDB(
        agent_id=agent_id,
        timestamp=datetime.fromisoformat(report.timestamp),
        audit=json.dumps(report.audit),
        integrity_alerts=json.dumps(report.integrity_alerts),
    )
    db.add(report_db)
    db.commit()
    db.close()
    return {"message": f"Report received for agent {agent_id}"}

# Route pour voir les derniers rapports
@app.get("/dashboard/{agent_id}")
def dashboard(agent_id: str, token_sub: str = Depends(verify_token)):
    # Optionnel: restreindre la visualisation si token_sub != agent_id ou admin
    db = SessionLocal()
    reports_db = db.query(ReportDB).filter(ReportDB.agent_id == agent_id).all()
    result = []
    for r in reports_db:
        result.append({
            "timestamp": r.timestamp.isoformat(),
            "audit": json.loads(r.audit),
            "integrity_alerts": json.loads(r.integrity_alerts) if r.integrity_alerts else None
        })
    db.close()
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
