# metrics_collector.py - extrae métricas de los archivos generados y guarda CSV
import os, glob, json, csv, time
LOGDIR = os.getenv('LOGDIR', '/data/logs')
METDIR = os.path.join(LOGDIR, 'metrics')
os.makedirs(METDIR, exist_ok=True)

def extract_runs():
    runs = sorted(glob.glob(os.path.join(LOGDIR, 'run_*.json')), reverse=True)
    if not runs:
        print('No run_ files found.')
        return
    latest = runs[0]
    with open(latest) as f:
        data = json.load(f)
    rows = []
    for entry in data:
        if 'result' in entry:
            r = entry['result']
            rows.append({'ts': r.get('session_ts'), 'N': r.get('N'), 'sift_len': r.get('sift_len'), 'qber': r.get('qber'), 'loss': r.get('loss'), 'error': r.get('error')})
    csvf = os.path.join(METDIR, f'metrics_{int(time.time())}.csv')
    with open(csvf, 'w', newline='') as csvfile:
        w = csv.DictWriter(csvfile, fieldnames=['ts','N','sift_len','qber','loss','error'])
        w.writeheader()
        w.writerows(rows)
    print(f'Metrics extracted to {csvf}')

if __name__ == '__main__':
    extract_runs()
