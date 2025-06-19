# Module de vérification d'intégrité des fichiers pour ShieldCLI
# Déplacé dans shieldcli/integrity/

# Ce script doit être déplacé dans shieldcli/integrity/ pour respecter l'organisation du projet.
# Après déplacement, lancez-le avec :
#   python shieldcli/integrity/file_monitor.py
# Les fichiers de config doivent rester accessibles à la racine ou être référencés correctement.

import time
import json
import os
import hashlib
import stat

def compute_checksum(file_path):
    """
    Calcule le hash SHA256 d'un fichier donné.
    Retourne le hash sous forme de chaîne hexadécimale, ou None en cas d'erreur.
    """
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256()
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except Exception as e:
        print(f"Erreur lors du calcul du checksum pour {file_path}: {e}")
        return None

def load_checksums(checksum_path):
    """
    Charge les checksums depuis un fichier JSON.
    Retourne un dictionnaire {chemin: checksum}.
    """
    if os.path.exists(checksum_path):
        with open(checksum_path, 'r') as f:
            try:
                return json.load(f).get('checksums', {})
            except Exception as e:
                print(f"Erreur lors du chargement des checksums: {e}")
                return {}
    return {}

def save_checksums(checksum_path, checksums):
    """ 
    Sauvegarde les checksums dans un fichier JSON.
    """
    try:
        with open(checksum_path, 'w') as f:
            json.dump({'checksums': checksums}, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des checksums: {e}")

def get_permissions(file_path):
    """
    Retroune les permissions du fichier sous forme d'entier (mode octal).
    """
    try:
        return oct(os.stat(file_path).st_mode & 0o777)
    except Exception as e:
        print(f"Erreur lors de la récupération des permissions pour {file_path}: {e}")
        return None

def run_integrity_check():
    """
    Fonction à appeler par l'agent pour obtenir les alertes d'intégrité et de permissions.
    Retourne une liste d'alertes (dictionnaires).
    """
    racine = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(racine, "monitor_config.json")
    checksum_path = os.path.join(racine, "checksums.json")
    permissions_path = os.path.join(racine, "permissions_ref.json")
    alerts = []
    if not os.path.exists(config_path):
        alerts.append({"type": "error", "msg": f"Fichier de configuration introuvable: {config_path}"})
        return alerts
    with open(config_path, "r") as f:
        try:
            config = json.load(f)
        except Exception as e:
            alerts.append({"type": "error", "msg": f"Erreur lecture config: {e}"})
            return alerts
    paths = config.get("paths", [])
    if not paths:
        alerts.append({"type": "error", "msg": "Aucun chemin à surveiller dans la config."})
        return alerts
    current_checksums = load_checksums(checksum_path)
    if os.path.exists(permissions_path):
        with open(permissions_path, "r") as f:
            permissions_ref = json.load(f).get("permissions", {})
    else:
        permissions_ref = {}
    for file_path, ref_checksum in current_checksums.items():
        if os.path.exists(file_path):
            new_checksum = compute_checksum(file_path)
            if new_checksum and new_checksum != ref_checksum:
                alerts.append({"type": "checksum", "file": file_path, "msg": "Modification détectée"})
            current_perms = get_permissions(file_path)
            ref_perms = permissions_ref.get(file_path)
            if ref_perms and current_perms and current_perms != ref_perms:
                alerts.append({"type": "permissions", "file": file_path, "msg": f"Permissions modifiées (réf: {ref_perms}, actuel: {current_perms})"})
        else:
            alerts.append({"type": "missing", "file": file_path, "msg": "Fichier manquant"})
    return alerts

if __name__ == "__main__":
    # Les fichiers de config sont à la racine du projet
    racine = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(racine, "monitor_config.json")
    checksum_path = os.path.join(racine, "checksums.json")

    if not os.path.exists(config_path):
        print(f"Fichier de configuration introuvable: {config_path}")
    else:
        with open(config_path, "r") as f:
            try:
                config = json.load(f)
            except Exception as e:
                print(f"Erreur lors de la lecture de la configuration: {e}")
                exit(1)
        paths = config.get("paths", [])
        if not paths:
            print("Aucun chemin à surveiller dans le fichier de configuration.")
        else:
            # Réinitialisation de la base de référence à chaque exécution
            checksums = {}
            permissions_ref = {}
            for path in paths:
                if os.path.isfile(path):
                    checksum = compute_checksum(path)
                    perms = get_permissions(path)
                    if checksum:
                        checksums[path] = checksum
                    if perms:
                        permissions_ref[path] = perms
                elif os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            checksum = compute_checksum(file_path)
                            perms = get_permissions(file_path)
                            if checksum:
                                checksums[file_path] = checksum
                            if perms:
                                permissions_ref[file_path] = perms
            save_checksums(checksum_path, checksums)
            # Sauvegarde des permissions de référence
            with open(os.path.join(racine, "permissions_ref.json"), "w") as f:
                json.dump({"permissions": permissions_ref}, f, indent=4)
            print("Base de référence des checksums et permissions réinitialisée.")

            # Vérification périodique des checksums et permissions
            try:
                while True:
                    time.sleep(10)  # Vérifie toutes les 10 secondes
                    current_checksums = load_checksums(checksum_path)
                    # Chargement des permissions de référence
                    with open(os.path.join(racine, "permissions_ref.json"), "r") as f:
                        permissions_ref = json.load(f).get("permissions", {})
                    for file_path, ref_checksum in current_checksums.items():
                        if os.path.exists(file_path):
                            new_checksum = compute_checksum(file_path)
                            if new_checksum and new_checksum != ref_checksum:
                                print(f"[ALERTE] Modification détectée (checksum) : {file_path}")
                            # Vérification des permissions
                            current_perms = get_permissions(file_path)
                            ref_perms = permissions_ref.get(file_path)
                            if ref_perms and current_perms and current_perms != ref_perms:
                                print(f"[ALERTE] Permissions modifiées : {file_path} (réf: {ref_perms}, actuel: {current_perms})")
                        else:
                            print(f"[ALERTE] Fichier manquant : {file_path}")
            except KeyboardInterrupt:
                print("Arrêt de la surveillance d'intégrité.")
