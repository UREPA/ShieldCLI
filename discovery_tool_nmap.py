import csv
import nmap  # Nécessite: pip install python-nmap
from manuf import manuf  # Nécessite: pip install manuf (pour identifier le fabricant d'un appareil)

# Fonction principale pour scanner les appareils sur une plage IP donnée
# et détecter l'OS et le fabricant via Nmap avec scan SYN pour OS detection
def scan(ip_range):
    nm = nmap.PortScanner()
    # Scan SYN (-sS) + détection d'OS (-O)
    nm.scan(hosts=ip_range, arguments='-sS -O')

    parser = manuf.MacParser()  # Pour identifier le fabricant via l'adresse MAC (OUI)
    actifs = []

    for host in nm.all_hosts():
        if nm[host].state() != 'up':
            continue

        ip = host
        # Récupère l'adresse MAC et le fabricant via nmap
        mac = nm[host]['addresses'].get('mac', 'Inconnu')
        device_type = parser.get_manuf(mac) if mac != 'Inconnu' else 'Inconnu'

        # Récupère le nom d'hôte si disponible via nmap
        hostname = nm[host]['hostnames'][0]['name'] if nm[host]['hostnames'] else 'Inconnu'

        # Récupère le nom de l'OS détecté par nmap
        os_guess = 'Inconnu'
        os_matches = nm[host].get('osmatch', [])
        if os_matches:
            os_guess = os_matches[0]['name']

        actifs.append({
            'ip': ip,
            'mac': mac,
            'hostname': hostname,
            'device_type': device_type,
            'os': os_guess
        })

    return actifs

# Fonction pour sauvegarder les résultats du scan dans un fichier CSV
def save_to_csv(data, filename="actifs_nmap.csv"):
    with open(filename, mode='w', newline='') as file:
        # Colonnes: IP, MAC, Hostname, Type d'appareil, OS détecté
        fieldnames = ["ip", "mac", "hostname", "device_type", "os"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()       # Écrit l'en-tête
        writer.writerows(data)     # Écrit chaque ligne à partir des données collectées

# Point d'entrée du script
if __name__ == "__main__":
    ip_range = "192.168.109.0/24"   # Plage IP à scanner (adapter selon ton réseau)
    actifs = scan(ip_range)           # Lancement du scan via nmap
    save_to_csv(actifs)               # Sauvegarde les résultats dans un fichier CSV
    print(f"{len(actifs)} appareils détectés et enregistrés dans 'actifs_nmap.csv'")
