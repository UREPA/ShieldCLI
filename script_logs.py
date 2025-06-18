import json
import os
import csv
import datetime
import re
import platform

try:
    import win32evtlog
except ImportError:
    win32evtlog = None

def load_config(path='config.json'):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_iso(dt_str):
    return datetime.datetime.fromisoformat(dt_str) if dt_str else None

def filter_line(line, since, until, keywords):
    try:
        parts = line.split()
        dt = datetime.datetime.strptime(
            f"{parts[0]} {parts[1]} {datetime.datetime.now().year} {parts[2]}",
            "%b %d %Y %H:%M:%S"
        )
    except Exception:
        dt = None
    if dt:
        if since and dt < since:
            return False
        if until and dt > until:
            return False
    if keywords and not any(re.search(kw, line, re.IGNORECASE) for kw in keywords):
        return False
    return True

# Logs Linux
def fetch_linux(cfg):
    since = parse_iso(cfg['filters'].get('since', ''))
    until = parse_iso(cfg['filters'].get('until', ''))
    keywords = cfg['filters'].get('keywords', [])
    data = []
    for path in cfg['logs']:
        if not os.path.isfile(path):
            print(f"Fichier introuvable: {path}")
            continue
        with open(path, 'r', errors='ignore') as f:
            for line in f:
                if filter_line(line, since, until, keywords):
                    data.append({'file': os.path.basename(path), 'line': line.strip()})
    return data

# Logs Windows
def fetch_windows(cfg):
    if not win32evtlog:
        raise RuntimeError("pywin32 non installé ou script exécuté sous Linux")
    server = cfg.get('server', None)
    since = parse_iso(cfg['filters'].get('since', ''))
    until = parse_iso(cfg['filters'].get('until', ''))
    keywords = cfg['filters'].get('keywords', [])
    data = []
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    for log in cfg['logs']:
        handle = win32evtlog.OpenEventLog(server, log)
        while True:
            recs = win32evtlog.ReadEventLog(handle, flags, 0)
            if not recs:
                break
            for ev in recs:
                t = ev.TimeGenerated
                if since and t < since:
                    win32evtlog.CloseEventLog(handle)
                    return data
                if until and t > until:
                    continue
                msg = win32evtlog.FormatMessage(ev)
                if keywords and not any(kw.lower() in msg.lower() for kw in keywords):
                    continue
                data.append({
                    'log': log,
                    'time': t.isoformat(sep=' '),
                    'source': ev.SourceName,
                    'event_id': ev.EventID & 0xFFFF,
                    'message': msg.replace('\r\n',' ')
                })
        win32evtlog.CloseEventLog(handle)
    return data

# Sauvegarde TXT ou CSV
def save(data, outcfg):
    if not data:
        print("Aucune entrée collectée.")
        return
    fmt = outcfg['format']
    base = outcfg['file']
    if fmt == 'txt':
        with open(base + '.txt', 'w', encoding='utf-8') as f:
            for entry in data:
                f.write(str(entry) + '\n')
    else:
        with open(base + '.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
    print(f"{len(data)} entrées enregistrées dans {base}.{fmt}")

if __name__ == '__main__':
    cfg = load_config()
    current_os = platform.system().lower()
    if current_os == 'windows':
        data = fetch_windows(cfg['windows'])
        outcfg = cfg['windows']['output']
    elif current_os == 'linux':
        data = fetch_linux(cfg['linux'])
        outcfg = cfg['linux']['output']
    else:
        print(f"OS non supporté: {current_os}")
        exit(1)
    save(data, outcfg)

