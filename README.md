# ShieldCLI

ShieldCLI est un outil de surveillance, d'intégrité et d'audit pour systèmes, pensé pour la cybersécurité.

## Fonctionnalités principales

### 1. Surveillance d'intégrité des fichiers (File Integrity Monitoring)
- Calcule et stocke un checksum de référence pour chaque fichier/dossier surveillé (SHA256).
- Vérifie périodiquement l'intégrité des fichiers : toute modification, suppression ou changement de permissions est détecté et signalé.
- Les chemins à surveiller sont définis dans `monitor_config.json`.
- Les alertes d'intégrité sont envoyées à l'API centrale.

### 2. Agent de remontée d'audit et d'intégrité
- `agent.py` collecte les résultats d'audit (`compliance_audit`) et les alertes d'intégrité, puis les envoie à l'API centrale avec authentification JWT.
- Les données sont stockées dans une base SQLite via l'API.

### 3. API centrale (FastAPI)
- Réceptionne les rapports des agents.
- Stocke les audits et alertes d'intégrité en base de données.
- Dashboard pour consulter les rapports par agent.

### 4. Déploiement Docker
- Un `Dockerfile` et un `docker-compose.yml` sont fournis pour lancer l'API dans un conteneur Docker.

---

## Installation et utilisation

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Lancer l'API centrale
```bash
# En local
uvicorn shieldcli.api:app --reload --host 0.0.0.0 --port 8000

# Ou avec Docker Compose
# (nécessite Docker installé)
docker compose up --build
```

### 3. Configurer l'agent
- Définir les chemins à surveiller dans `monitor_config.json`.
- Lancer l'agent pour envoyer un rapport :
```bash
python agent.py
```

### 4. Lancer la vérification d'intégrité seule
```bash
python shieldcli/integrity/file_monitor.py
```

---

## Organisation du projet
- `agent.py` : agent principal, envoie les rapports à l'API
- `shieldcli/api.py` : API FastAPI centrale
- `shieldcli/integrity/file_monitor.py` : vérification d'intégrité
- `shieldcli/compliance/compliance_audit.py` : audit de conformité
- `monitor_config.json`, `permissions_ref.json` : fichiers de config
- `requirements.txt`, `Dockerfile`, `docker-compose.yml` : à la racine

## Auteur
Groupe 1 - ISRC 