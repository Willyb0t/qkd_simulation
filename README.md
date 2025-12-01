# Simulación QKD con Docker (enfoque simple)

Estructura:
- docker-compose.yml         : define 3 servicios (bob, orchestrator, metrics)
- bob.py                     : proceso receptor (escucha por TCP)
- alice.py                   : emisor BB84 (se ejecuta desde orchestrator)
- orchestrator.py            : lanza experiments (ejecuta alice) y consolida JSON
- qkd_common.py              : utilidades (bits, bases, measure, qber)
- metrics_collector.py       : extrae métricas y genera CSV
- logs/                      : carpeta montada para persistir logs

Requisitos (host):
- Docker y Docker Compose
  sudo apt update
  sudo apt install -y docker.io docker-compose
  sudo usermod -aG docker $USER   # luego cerrar sesión o reboot

Ejecución rápida:
1) Clone o copie este proyecto en su máquina host.
2) Desde la carpeta del proyecto, levante los contenedores:
   sudo docker-compose up --build
3) El servicio 'orchestrator' ejecutará una serie de experimentos (alice->bob). Bob queda escuchando continuamente.
4) Los JSON de sesión y los resultados consolidados se guardan en ./logs/
5) Para extraer métricas en CSV, levante el servicio 'metrics' (ya está configurado en docker-compose) o ejecute manualmente:
   python3 metrics_collector.py

Ver logs (host):
  ls -lah logs/
  tail -f logs/alice_session_*.json
  tail -f logs/bob_session_*.json
  ls logs/metrics/
