import csv
import socket
from scapy.all import ARP, Ether, srp
from manuf import manuf 

def scan(ip_range):
    pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    
    result = srp(pkt, timeout=2, verbose=0)[0]

    parser = manuf.MacParser()
    actifs = []

    for _, received in result:
        ip = received.psrc       
        mac = received.hwsrc     

        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            hostname = "Inconnu"

        device_type = parser.get_manuf(mac) or "Inconnu"

        actifs.append({
            'ip': ip,
            'mac': mac,
            'hostname': hostname,
            'device_type': device_type
        })

    return actifs

def save_to_csv(data, filename="actifs.csv"):
    with open(filename, mode='w', newline='') as file:
   
        writer = csv.DictWriter(file, fieldnames=["ip", "mac", "hostname", "device_type"])
        writer.writeheader()       
        writer.writerows(data)     

if __name__ == "__main__":
    ip_range = "192.168.109.0/24"     
    actifs = scan(ip_range)         
    save_to_csv(actifs)             
    print(f"{len(actifs)} appareils détectés et enregistrés dans 'actifs.csv'")
