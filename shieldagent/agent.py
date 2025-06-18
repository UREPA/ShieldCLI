import time
import requests
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shieldcli.integrity import file_monitor

API_URL = "http://localhost:5000"
TOKEN_FILE = "agent_token.txt"

def collect_integrity():
    return {
        "feature": "integrity",
        "alerts": file_monitor.run_integrity_check()
    }

def collect_logs():
    # TODO: implémenter la collecte de logs
    return {"feature": "logs", "alerts": []}

def collect_compliance():
    # TODO: implémenter la vérification de compliance
    return {"feature": "compliance", "alerts": []}

def get_hostname():
    return os.uname().nodename if hasattr(os, 'uname') else os.getenv('COMPUTERNAME', 'unknown')

def get_token():
    # Si le token existe déjà, le lire
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    # Sinon, s'enregistrer auprès de l'API
    try:
        resp = requests.post(f"{API_URL}/register", json={"hostname": get_hostname()})
        print("[Agent] Réponse API /register:", resp.status_code, resp.text)
        token = None
        try:
            token = resp.json().get("token")
        except Exception as e:
            print("[Agent] Erreur lors du décodage JSON:", e)
        if token:
            with open(TOKEN_FILE, "w") as f:
                f.write(token)
        return token
    except Exception as e:
        print(f"[Agent] Erreur lors de l'enregistrement : {e}")
        return None

if __name__ == "__main__":
    token = get_token()
    if not token:
        print("[Agent] Impossible de récupérer un token JWT, arrêt.")
        exit(1)
    while True:
        data = {
            "hostname": get_hostname(),
            "integrity": collect_integrity(),
            "logs": collect_logs(),
            "compliance": collect_compliance()
        }
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.post(f"{API_URL}/report", json=data, headers=headers, timeout=5)
            print(f"[Agent] Données envoyées : {resp.status_code}")
        except Exception as e:
            print(f"[Agent] Erreur d'envoi : {e}")
        time.sleep(60)  # Envoi toutes les 60 secondes
