# bob.py - receptor simple para la simulación BB84 (escucha por TCP)
import socket, json, os, time
from qkd_common import random_bases, measure, timestamp, unique_id

LOGDIR = os.getenv('LOGDIR', '/data/logs')
os.makedirs(LOGDIR, exist_ok=True)

def run_bob(listen_host='0.0.0.0', listen_port=9001):
    print(f"[{timestamp()}] Bob: escuchando en {listen_host}:{listen_port}")
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((listen_host, listen_port))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        print(f"[{timestamp()}] Bob: conexion desde {addr}")
        data = b''
        while True:
            part = conn.recv(65536)
            if not part:
                break
            data += part
        try:
            payload = json.loads(data.decode())
        except Exception as e:
            payload = {}
        alice_bits = payload.get('bits', [])
        alice_bases = payload.get('bases', [])
        loss = payload.get('meta', {}).get('loss', 0.0)
        error = payload.get('meta', {}).get('error', 0.0)
        bases = random_bases(len(alice_bits))
        measures = []
        for i in range(len(alice_bits)):
            bit = alice_bits[i]
            send_basis = alice_bases[i] if i < len(alice_bases) else 'Z'
            meas = measure(bit, send_basis, bases[i], loss_prob=loss, error_prob=error)
            measures.append(meas)
        resp = {'bases': bases, 'measures': measures, 'meta': {'ts': timestamp(), 'N': len(alice_bits), 'loss': loss, 'error': error}}
        try:
            conn.sendall(json.dumps(resp).encode())
            conn.shutdown(socket.SHUT_WR)  # <-- aquí
            print("Bob: terminé de enviar y cerré el canal de escritura")

        except OSError:
            # El socket ya fue cerrado por Alice: ignorar
            pass
        finally:
            conn.close()

        # guardar log
        fname = os.path.join(LOGDIR, f'bob_session_{unique_id()}.json')
        with open(fname, 'w') as f:
            json.dump({'payload': payload, 'response': resp}, f, indent=2)
        print(f"[{timestamp()}] Bob: sesión guardada en {fname}")

if __name__ == '__main__':
    run_bob()
