import json
import csv
from datetime import datetime
import re
import os


def load_config(path='config.json'):
    with open(path) as f:
        return json.load(f)


def parse_line_date(line):
    # Extrait date d'une ligne de log au format 'Mmm dd HH:MM:SS'
    try:
        # Exemple syslog: 'Jun 17 14:33:01 hostname service: message'
        parts = line.split()
        mon = parts[0]
        day = parts[1]
        time_str = parts[2]
        year = datetime.now().year
        dt = datetime.strptime(f"{mon} {day} {year} {time_str}", "%b %d %Y %H:%M:%S")
        return dt
    except Exception:
        return None


def filter_line(line, cfg):
    dt = parse_line_date(line)
    if dt:
        if cfg['filters'].get('since'):
            since = datetime.fromisoformat(cfg['filters']['since'])
            if dt < since:
                return False
        if cfg['filters'].get('until'):
            until = datetime.fromisoformat(cfg['filters']['until'])
            if dt > until:
                return False
    # mots clés
    if cfg['filters'].get('keywords'):
        if not any(re.search(kw, line, re.IGNORECASE) for kw in cfg['filters']['keywords']):
            return False
    return True


def collect_logs(cfg):
    collected = []
    for path in cfg['logs']:
        if not os.path.isfile(path):
            print(f"Fichier introuvable: {path}")
            continue
        with open(path, 'r', errors='ignore') as f:
            for line in f:
                if filter_line(line, cfg):
                    collected.append({'file': os.path.basename(path), 'line': line.rstrip()})
    return collected


def save_txt(data, filename):
    with open(filename + '.txt', 'w') as f:
        for entry in data:
            f.write(f"[{entry['file']}] {entry['line']}\n")


def save_csv(data, filename):
    with open(filename + '.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'line'])
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)


def main():
    cfg = load_config()
    data = collect_logs(cfg)
    out = cfg['output']
    if out['format'] == 'txt':
        save_txt(data, out['file'])
    else:
        save_csv(data, out['file'])
    print(f"{len(data)} lignes de log collectées dans {out['file']}.{out['format']}")


if __name__ == '__main__':
    main()
