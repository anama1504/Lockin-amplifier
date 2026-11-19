from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from backend2 import SimulatedBackend, PHASE
from lockin2 import LockInAmplifier

F_REF = 50_000
DURATION = 0.5
FILTER_CUTOFF = 500      # Hz: compromiso entre ruido y retardo (la envolvente es de 5 Hz)
OUTPUT_RATE = 10_000

# 1-2. Crear el backend y generar la señal ruidosa
backend = SimulatedBackend(raw_sample_rate=1_000_000, reference_frequency=F_REF)
# Posible mejora: elegir el ruido al crear el backend, en vez de editar NOISE_STD en backend2.py
# backend = SimulatedBackend(raw_sample_rate=1_000_000, reference_frequency=F_REF, noise_std=5.0)
t_raw, v_raw = backend.generate_data(duration=DURATION)

# 3-4. Configurar el lock-in y demodular
lockin = LockInAmplifier(
    reference_frequency=F_REF,
    filter_cutoff=FILTER_CUTOFF,
    output_sample_rate=OUTPUT_RATE,
)
result = lockin.process(t_raw, v_raw)

# --- Alternativa con la interfaz común measure() (ver hardware_zi.py) -------------------------
# Así el programa no sabe si detrás hay software o un equipo real:
#
#   from hardware_zi import SoftwareLockIn, ZILockIn
#   fuente = SoftwareLockIn(backend, lockin)                           # <- única línea que elige qué hay detrás
#   # fuente = ZILockIn("DEV1234", F_REF, FILTER_CUTOFF, OUTPUT_RATE)  # <- con un equipo de Zurich
#   result = fuente.measure(duration=DURATION)                         # sustituye a generate_data + process
#
# Ojo: con measure() no tenemos t_raw ni v_raw, así que la gráfica de la señal cruda
# (más abajo) no se podría dibujar. Un equipo real tampoco entrega la señal cruda.
# ----------------------------------------------------------------------------------------------

# 5. Comparar R con la envolvente real, ignorando el transitorio inicial del filtro
envolvente = backend.envelope(result["t"])
tau = 1 / (2 * np.pi * FILTER_CUTOFF)
valido = result["t"] > 5 * tau   # valido es una máscara: una lista de True/False, del mismo tamaño que result["t"], que vale True donde el tiempo supera 5τ.

error = result["r"][valido] - envolvente[valido]
rmse = np.sqrt(np.mean(error ** 2))
print(f"RMSE entre R y A(t): {rmse:.4f}")
print(f"DC medio recuperado: {np.mean(result['dc'][valido]):.3f}")
print(f"Fase media recuperada: {np.rad2deg(np.mean(result['theta'][valido])):.1f}° (real {np.rad2deg(PHASE):.1f}°)")

# 6. Gráficas
fig, ax = plt.subplots(3, 1, figsize=(10, 9))

zoom = t_raw < 200e-6    # La señal oscila a 50 khz (fref). T=20us. 10T 
ax[0].plot(t_raw[zoom] * 1e6, v_raw[zoom])
ax[0].set(title="Señal cruda con ruido (200 µs)", xlabel="t (µs)", ylabel="V")

ax[1].plot(result["t"], result["r"])
ax[1].set(title="Magnitud recuperada R", xlabel="t (s)", ylabel="V")

ax[2].plot(result["t"], result["r"], label="R recuperada")
ax[2].plot(result["t"], envolvente, "--", label="Envolvente real A(t)")
ax[2].set(title=f"Comparación (RMSE = {rmse:.3f})", xlabel="t (s)", ylabel="V")
ax[2].legend()

fig.tight_layout()
plt.savefig(Path(__file__).parent / "figuras" / "demo2_resultados.png", dpi=120)
plt.show()
