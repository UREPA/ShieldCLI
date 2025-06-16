import time
import json
import os
import hashlib

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

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "monitor_config.json")
    checksum_path = os.path.join(os.path.dirname(__file__), "checksums.json")

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
            for path in paths:
                if os.path.isfile(path):
                    checksum = compute_checksum(path)
                    if checksum:
                        checksums[path] = checksum
                elif os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            checksum = compute_checksum(file_path)
                            if checksum:
                                checksums[file_path] = checksum
            save_checksums(checksum_path, checksums)
            print("Base de référence des checksums réinitialisée.")

            # Vérification périodique des checksums
            try:
                while True:
                    time.sleep(10)  # Vérifie toutes les 10 secondes
                    current_checksums = load_checksums(checksum_path)
                    for file_path, ref_checksum in current_checksums.items():
                        if os.path.exists(file_path):
                            new_checksum = compute_checksum(file_path)
                            if new_checksum and new_checksum != ref_checksum:
                                print(f"[ALERTE] Modification détectée (checksum) : {file_path}")
                        else:
                            print(f"[ALERTE] Fichier manquant : {file_path}")
            except KeyboardInterrupt:
                print("Arrêt de la surveillance d'intégrité.")
