# alice.py - emisor simple para BB84 (conecta a Bob por TCP)
import socket, json, os, time, argparse
from qkd_common import random_bits, random_bases, compute_qber, timestamp, unique_id

LOGDIR = os.getenv('LOGDIR', '/data/logs')
os.makedirs(LOGDIR, exist_ok=True)

def run_alice(bob_host='bob', bob_port=9001, N=1024, loss=0.01, error=0.005):
    print(f"[{timestamp()}] Alice: iniciando experimento N={N} loss={loss} error={error} -> Bob={bob_host}:{bob_port}")

    bits = random_bits(N)
    bases = random_bases(N)
    payload = {
        'bits': bits,
        'bases': bases,
        'meta': {'loss': loss, 'error': error, 'N': N, 'ts': timestamp()}
    }

    s = socket.socket()
    s.settimeout(20)
    try:
        s.connect((bob_host, bob_port))
        s.sendall(json.dumps(payload).encode())
        s.shutdown(socket.SHUT_WR)

        # ←------------------ FIX AQUÍ -------------------→
        data = b''
        while True:
            chunk = s.recv(65536)
            if not chunk:
                print("Alice: recibí FIN DE TRANSMISIÓN (chunk vacío)")
                break
            data += chunk
        # ←------------------------------------------------→

        resp = json.loads(data.decode())

    finally:
        s.close()

    bob_bases = resp.get('bases', [])
    bob_measures = resp.get('measures', [])

    sift_a = []
    sift_b = []
    for i in range(min(len(bases), len(bob_bases))):
        if bases[i] == bob_bases[i] and bob_measures[i] is not None:
            sift_a.append(bits[i])
            sift_b.append(bob_measures[i])

    qber = compute_qber(sift_a, sift_b) if sift_a else None

    result = {
        'session_ts': timestamp(),
        'N': N,
        'sift_len': len(sift_a),
        'qber': qber,
        'loss': loss,
        'error': error
    }

    fname = os.path.join(LOGDIR, f'alice_session_{unique_id()}.json')
    with open(fname, 'w') as f:
        json.dump({'payload': payload, 'response': resp, 'result': result}, f, indent=2)

    print(f"[{timestamp()}] Alice: resultado guardado en {fname}")
    print(f"[{timestamp()}] Alice: QBER={qber} sift_len={len(sift_a)}")

    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bob', default='bob')
    parser.add_argument('--port', type=int, default=9001)
    parser.add_argument('--n', type=int, default=1024)
    parser.add_argument('--loss', type=float, default=0.01)
    parser.add_argument('--error', type=float, default=0.005)
    args = parser.parse_args()
    run_alice(args.bob, args.port, args.n, args.loss, args.error)
