import csv
import socket
from scapy.all import get_if_addr, get_if_hwaddr
from manuf import manuf

# Récupère l'adresse IP locale en utilisant l'interface par défaut
def get_local_ip():
    return get_if_addr("eth0")  # ou remplace "eth0" par ton interface, ou utilise scapy.conf.iface

# Récupère l'adresse MAC de la même interface
def get_local_mac():
    return get_if_hwaddr("eth0")  # idem pour l'interface

# Fonction principale : collecte les infos de la machine locale
def scan_local_scapy():
    ip = get_local_ip()
    mac = get_local_mac()

    # Nom d'hôte via DNS inverse
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = socket.gethostname()

    # Type d'appareil/fabricant via OUI
    parser = manuf.MacParser()
    device_type = parser.get_manuf(mac) or "Inconnu"

    return [{
        'ip': ip,
        'mac': mac,
        'hostname': hostname,
        'device_type': device_type
    }]

# Sauvegarde dans CSV
def save_to_csv(data, filename="local_actifs.csv"):
    with open(filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["ip", "mac", "hostname", "device_type"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    data = scan_local_scapy()
    save_to_csv(data)
    print(f"{len(data)} entrée(s) locale(s) enregistrée(s) dans 'local_actifs.csv'")
