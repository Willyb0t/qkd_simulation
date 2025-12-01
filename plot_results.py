import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

# --- CONFIGURACIÓN ---
METRICS_DIR = './logs/metrics'  # Asegúrate que esta ruta coincida con tu carpeta
# ---------------------

def load_latest_csv(folder):
    list_of_files = glob.glob(os.path.join(folder, '*.csv'))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

csv_file = load_latest_csv(METRICS_DIR)
if not csv_file:
    print(f"Error: No se encontraron archivos .csv en {METRICS_DIR}")
    exit()

print(f"Procesando: {csv_file}")
df = pd.read_csv(csv_file)

# Calcular Tasa de Clave (Yield) normalizada
df['key_rate'] = df['sift_len'] / df['N']

# Preparar figura con 2 subgráficas
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# ==============================================================================
# GRÁFICA 1: Validación de QBER (Input Error vs Output QBER)
# ==============================================================================
# Agrupamos por 'loss' para ver si la pérdida afecta el error (no debería)
losses = sorted(df['loss'].unique())

# Línea Ideal (x=y)
max_err = df['error'].max()
ax1.plot([0, max_err], [0, max_err], 'k--', alpha=0.5, label='Ideal (x=y)')

for loss_val in losses:
    subset = df[df['loss'] == loss_val]
    # Pintamos cada grupo de pérdida con un color distinto
    ax1.scatter(subset['error'], subset['qber'], 
                alpha=0.7, s=60, label=f'Loss={loss_val}')

ax1.set_title('Validación de Ruido (QBER)')
ax1.set_xlabel('Probabilidad de Error Inyectada (Input)')
ax1.set_ylabel('QBER Medido (Output)')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend(title="Pérdida (Loss)")


# ==============================================================================
# GRÁFICA 2: Rendimiento (Loss vs Key Rate)
# ==============================================================================
# Agrupamos por 'error' para ver si el ruido afecta el tamaño de clave
errors = sorted(df['error'].unique())

# Línea Teórica: Yield = 0.5 * (1 - loss)
# BB84 descarta el 50% por bases incompatibles, y luego resta la pérdida
x_theory = np.linspace(df['loss'].min(), df['loss'].max(), 100)
y_theory = 0.5 * (1 - x_theory)
ax2.plot(x_theory, y_theory, 'k--', alpha=0.5, label='Teórico (0.5 * (1-loss))')

for err_val in errors:
    subset = df[df['error'] == err_val]
    # Ordenamos para que la línea se dibuje bien
    subset = subset.sort_values(by='loss')
    ax2.plot(subset['loss'], subset['key_rate'], 'o-', alpha=0.7, label=f'Error={err_val}')

ax2.set_title('Rendimiento del Canal (Tasa de Clave)')
ax2.set_xlabel('Pérdida del Canal (Loss)')
ax2.set_ylabel('Tasa de Clave (Bits Útiles / Bits Totales)')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(title="Error Inyectado")

# Guardar y mostrar
plt.tight_layout()
output_file = 'analisis_completo_qkd.png'
plt.savefig(output_file)
print(f"Gráfica guardada en: {output_file}")
plt.show()