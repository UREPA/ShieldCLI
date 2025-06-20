from datetime import datetime, timezone
import os
import requests
import uuid

from shieldcli.compliance.compliance_audit import audit_checks
from shieldcli.integrity.file_monitor import run_integrity_check
from shieldcli.Discovery.Discovery_tool_nmap import scan_local
from shieldcli.Discovery.Discovery_tool_scapy import scan_local_scapy
from shieldcli.logs.script_logs_multiOS_detect import fetch_linux, fetch_windows

AGENT_ID_FILE = "agent_id.txt"

API_URL = "http://192.168.126.1:8000/report"
LOGIN_URL = "http://192.168.126.1:8000/login"

HEADERS = {
    "Content-Type": "application/json"
}

def get_agent_id():
    if os.path.exists(AGENT_ID_FILE):
        with open(AGENT_ID_FILE, "r") as f:
            return f.read().strip()
    else:
        new_id = str(uuid.uuid4())
        with open(AGENT_ID_FILE, "w") as f:
            f.write(new_id)
        return new_id

# Obtenir un token JWT valide via la route /login
def get_jwt_token(agent_id):
    try:
        r = requests.post(LOGIN_URL, json={"agent_id": agent_id})
        r.raise_for_status()
        token = r.json().get("access_token")
        return token
    except Exception as e:
        print("Erreur login:", e)
        return None

# Envoi vers API
def send_report():
    # Récupérer un token JWT valide avant l'envoi
    agent_id = get_agent_id()
    token = get_jwt_token(agent_id)
    if not token:
        print("Impossible d'obtenir un token JWT")
        return

    # Mettre à jour le header Authorization avec le token JWT
    HEADERS["Authorization"] = f"Bearer {token}"

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit": audit_checks(),
        "integrity_alerts": run_integrity_check(),
        "scan_nmap": scan_local(),
        "scan_scapy": scan_local_scapy(),
        "logs_linux": fetch_linux(),
        "logs_windows": fetch_windows()
    }

    try:
        r = requests.post(API_URL, headers=HEADERS, json=data)
        print("Statut:", r.status_code)
    except Exception as e:
        print("Erreur lors de l'envoi:", e)

if __name__ == "__main__":
    send_report()
