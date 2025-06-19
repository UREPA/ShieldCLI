import csv
import socket
import nmap           # pip install python-nmap
from manuf import manuf  # pip install manuf

def get_local_ip():
    """Récupère l'IP primaire de la machine en ouvrant une socket UDP."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # l'adresse 8.8.8.8 n'est jamais jointe réellement, c'est juste pour déterminer l'interface
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def scan_local():
    local_ip = get_local_ip()
    nm = nmap.PortScanner()
    # Scan SYN + OS detection sur l'hôte local
    nm.scan(hosts=local_ip, arguments='-sS -O')

    parser = manuf.MacParser()
    result = []

    host_info = nm.all_hosts()[0]  # il n'y a qu'un seul host
    if nm[host_info].state() != 'up':
        print("L'hôte local n'est pas détecté comme 'up'.")
        return result

    mac = nm[host_info]['addresses'].get('mac', 'Inconnu')
    device_type = parser.get_manuf(mac) if mac != 'Inconnu' else 'Inconnu'
    hostname = nm[host_info]['hostnames'][0]['name'] if nm[host_info]['hostnames'] else socket.gethostname()

    os_guess = 'Inconnu'
    os_matches = nm[host_info].get('osmatch', [])
    if os_matches:
        os_guess = os_matches[0]['name']

    result.append({
        'ip': local_ip,
        'mac': mac,
        'hostname': hostname,
        'device_type': device_type,
        'os': os_guess
    })
    return result

def save_to_csv(data, filename="local_asset.csv"):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["ip","mac","hostname","device_type","os"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    data = scan_local()
    if data:
        save_to_csv(data)
        print(f"{len(data)} machine locale analysée et enregistrée dans 'local_asset.csv'")
    else:
        print("Aucun résultat.")    
