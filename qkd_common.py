# qkd_common.py - utilidades compartidas para la simulación BB84 simplificada
import secrets, time, os

def random_bits(n):
    return [secrets.randbelow(2) for _ in range(n)]

def random_bases(n):
    return [secrets.choice(['Z','X']) for _ in range(n)]

def measure(bit, send_basis, meas_basis, loss_prob=0.0, error_prob=0.0):
    # Return None on loss, otherwise a measured bit 0/1 (simulate noise)
    if secrets.randbelow(1_000_000) / 1_000_000 < loss_prob:
        return None
    measured = bit
    if secrets.randbelow(1_000_000) / 1_000_000 < error_prob:
        measured = 1 - bit
    if send_basis != meas_basis:
        return secrets.randbelow(2)
    return measured

def compute_qber(alice_key, bob_key):
    if not alice_key:
        return None
    errors = sum(1 for a,b in zip(alice_key, bob_key) if a!=b)
    return errors / len(alice_key)

def timestamp():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def unique_id():
    """Genera un ID único con microsegundos para evitar colisiones"""
    return int(time.time() * 1_000_000)
