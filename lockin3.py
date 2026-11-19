"""Versión de lockin2.py que procesa la señal por bloques (menos memoria, mismo resultado).

Es una copia de lockin2.py: la clase y los métodos se llaman igual, así que para probarla
basta con cambiar el import en demo2.py:

    from lockin3 import LockInAmplifier
"""
import numpy as np
from scipy import signal


class LockInAmplifier:
    def __init__(objeto, reference_frequency, filter_cutoff, output_sample_rate, block_size=200_000):
        objeto.reference_frequency = reference_frequency
        objeto.filter_cutoff = filter_cutoff
        objeto.output_sample_rate = output_sample_rate
        objeto.block_size = block_size      # muestras crudas que se procesan de una vez

    def process(objeto, t_raw, v_raw):
        fs = 1 / (t_raw[1] - t_raw[0])
        N = round(fs / objeto.output_sample_rate)      # decimación: nos quedamos con 1 de cada N

        # El tamaño del bloque tiene que ser múltiplo de N para que el "1 de cada N"
        # caiga en los mismos puntos que si se procesara todo junto.
        bloque = max(N, objeto.block_size // N * N)

        # Filtro paso bajo (se diseña una vez y se aplica a los tres canales)
        sos = signal.butter(4, objeto.filter_cutoff, btype="low", fs=fs, output="sos")

        # "Memoria" del filtro de cada canal: permite continuar donde se quedó el bloque anterior
        zi_x = np.zeros((sos.shape[0], 2))
        zi_y = np.zeros((sos.shape[0], 2))
        zi_dc = np.zeros((sos.shape[0], 2))

        t_salida, x_salida, y_salida, dc_salida = [], [], [], []

        for inicio in range(0, len(v_raw), bloque):
            t = t_raw[inicio:inicio + bloque]
            v = v_raw[inicio:inicio + bloque]

            # Mezclado: la fase de la referencia sigue el tiempo real, no el del bloque
            seno = np.sin(2 * np.pi * objeto.reference_frequency * t)
            coseno = np.cos(2 * np.pi * objeto.reference_frequency * t)

            # Filtrado: se pasa y se recoge el estado para que no haya saltos entre bloques
            x_filtrado, zi_x = signal.sosfilt(sos, v * seno, zi=zi_x)
            y_filtrado, zi_y = signal.sosfilt(sos, v * coseno, zi=zi_y)
            dc_filtrado, zi_dc = signal.sosfilt(sos, v, zi=zi_dc)    # sin mezclar, sin factor 2

            # Decimación inmediata: guardamos 1 de cada N y descartamos el resto
            t_salida.append(t[::N])
            x_salida.append(2 * x_filtrado[::N])    # el 2 compensa el 1/2 del producto
            y_salida.append(2 * y_filtrado[::N])
            dc_salida.append(dc_filtrado[::N])

        t = np.concatenate(t_salida)
        x = np.concatenate(x_salida)
        y = np.concatenate(y_salida)
        dc = np.concatenate(dc_salida)

        R = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)

        return {"t": t, "x": x, "y": y, "r": R, "theta": theta, "dc": dc}
