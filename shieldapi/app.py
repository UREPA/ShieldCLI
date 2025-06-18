from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from jose import jwt, JWTError
import secrets

app = FastAPI()

# Initialisation de la base SQLite shielddb.sqlite3
engine = create_engine('sqlite:///shielddb.sqlite3')
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"

class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(128))
    feature = Column(String(32))
    alerts = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(128), unique=True, index=True)
    registered_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

@app.post("/register")
async def register_agent(request: Request):
    try:
        body = await request.body()
        print(f"[API] Body brut reçu : {body}")
        try:
            data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Requête JSON invalide")
        hostname = data.get("hostname", "unknown")
        session = SessionLocal()
        agent = session.query(Agent).filter_by(hostname=hostname).first()
        if not agent:
            agent = Agent(hostname=hostname)
            session.add(agent)
            session.commit()
        token = jwt.encode({"hostname": hostname}, SECRET_KEY, algorithm=ALGORITHM)
        session.close()
        print(f"[API] Agent enregistré: {hostname}")
        return {"token": token}
    except Exception as e:
        print("[API] Erreur dans /register:", e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def verify_jwt(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant ou invalide")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

@app.post("/report")
async def receive_report(request: Request, payload=Depends(verify_jwt)):
    data = await request.json()
    print(f"Reçu : {data}")
    session = SessionLocal()
    # Pour chaque feature, stocker un rapport
    for feature in ["integrity", "logs", "compliance"]:
        if feature in data:
            alerts = data[feature].get("alerts", [])
            report = Report(
                hostname=data.get("hostname", payload.get("hostname", "unknown")),
                feature=feature,
                alerts=json.dumps(alerts)
            )
            session.add(report)
    session.commit()
    session.close()
    return JSONResponse(content={"status": "ok"})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
