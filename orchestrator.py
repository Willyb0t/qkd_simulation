# orchestrator.py - lanza experimentos y consolida resultados
import subprocess, time, os, json, glob
from qkd_common import timestamp, unique_id

LOGDIR = os.getenv('LOGDIR', '/data/logs')
os.makedirs(LOGDIR, exist_ok=True)

def run_experiment(bob_host='bob', n=1024, loss=0.01, error=0.005):
    # ejecuta alice localmente (orquestador) apuntando a servicio 'bob'
    alice_cmd = ['python','alice.py','--bob',bob_host,'--n',str(n),'--loss',str(loss),'--error',str(error)]
    p = subprocess.run(alice_cmd, capture_output=True, text=True)
    print(p.stdout)
    # consolidar archivos JSON en un run_ timestamp
    entries = []
    for fname in os.listdir(LOGDIR):
        if fname.endswith('.json') and ('alice_session' in fname or 'bob_session' in fname):
            with open(os.path.join(LOGDIR, fname)) as f:
                try:
                    entries.append(json.load(f))
                except:
                    pass
    outf = os.path.join(LOGDIR, f'run_{int(time.time())}.json')
    with open(outf, 'w') as f:
        json.dump(entries, f, indent=2)
    print(f"[orchestrator] Experimento completado. Resultado: {outf}")

def orchestrate():
    print(f"[{timestamp()}] Orchestrator: iniciando recolección de sesiones")
    time.sleep(2)  # Esperar a que Alice y Bob terminen
    
    alice_sessions = sorted(glob.glob(os.path.join(LOGDIR, 'alice_session_*.json')))
    bob_sessions = sorted(glob.glob(os.path.join(LOGDIR, 'bob_session_*.json')))
    
    print(f"[{timestamp()}] Orchestrator: encontradas {len(alice_sessions)} sesiones Alice y {len(bob_sessions)} sesiones Bob")
    
    results = []
    for alice_file in alice_sessions:
        with open(alice_file) as f:
            alice_data = json.load(f)
        if 'result' in alice_data:
            results.append({'result': alice_data['result']})
    
    if results:
        run_file = os.path.join(LOGDIR, f'run_{unique_id()}.json')
        with open(run_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"[{timestamp()}] Orchestrator: agregación guardada en {run_file}")
    else:
        print(f"[{timestamp()}] Orchestrator: sin resultados para agregar")

if __name__ == '__main__':
    # ejecutar varias rondas con parámetros distintos
    params = [
        (1024, 0.01, 0.005),
        (2048, 0.02, 0.01),
        (1024, 0.05, 0.02)
    ]
    for n, loss, error in params:
        run_experiment('bob', n, loss, error)
        time.sleep(2)
    orchestrate()
