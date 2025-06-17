import csv
import nmap  
from manuf import manuf  

def scan(ip_range):
    nm = nmap.PortScanner()
    
    nm.scan(hosts=ip_range, arguments='-sS -O')

    parser = manuf.MacParser()  
    actifs = []

    for host in nm.all_hosts():
        if nm[host].state() != 'up':
            continue

        ip = host
        # Récupère l'adresse MAC et le fabricant via nmap
        mac = nm[host]['addresses'].get('mac', 'Inconnu')
        device_type = parser.get_manuf(mac) if mac != 'Inconnu' else 'Inconnu'

        # Récupère le nom d'hôte via nmap
        hostname = nm[host]['hostnames'][0]['name'] if nm[host]['hostnames'] else 'Inconnu'

        # Récupère le nom de l'OS 
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

def save_to_csv(data, filename="actifs_nmap.csv"):
    with open(filename, mode='w', newline='') as file:
       
        fieldnames = ["ip", "mac", "hostname", "device_type", "os"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()       
        writer.writerows(data)     

# Point d'entrée du script
if __name__ == "__main__":
    ip_range = "192.168.109.0/24"   
    actifs = scan(ip_range)           
    save_to_csv(actifs)            
    print(f"{len(actifs)} appareils détectés et enregistrés dans 'actifs_nmap.csv'")
