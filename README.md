# ShieldCLI

ShieldCLI est un outil de surveillance et d'intégrité pour systèmes, pensé pour la cybersécurité et l'audit.

## Fonctionnalités

### 1. Surveillance d'intégrité des fichiers (File Integrity Monitoring)
- Calcule et stocke un checksum de référence pour chaque fichier/dossier surveillé (SHA256).
- Vérifie périodiquement l'intégrité des fichiers : toute modification ou suppression est détectée et signalée.
- Les chemins à surveiller sont définis dans `monitor_config.json`.
- La base de référence est réinitialisée à chaque exécution.

#### Utilisation
```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer les chemins à surveiller dans monitor_config.json

# 3. Lancer la surveillance
python file_monitor.py
```

### 2. Vérification des logs (à venir)
*Fonctionnalité prévue : analyse et détection d'événements suspects dans les fichiers de logs système ou applicatifs.*

### 3. Vérification de la compliance (ISO, RGPD, etc.) (à venir)
*Fonctionnalité prévue : contrôle de conformité par rapport à des standards (ISO 27001, RGPD, etc.), génération de rapports d'audit.*

---

## À venir
- Ajout de la surveillance des logs
- Ajout de la vérification de conformité
- Améliorations de l'interface CLI

## Auteur
Projet pédagogique ISRC - Ingénieur systèmes réseau cybersécurité