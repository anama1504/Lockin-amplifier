
import numpy as np
from scipy import signal


class LockInAmplifier:
    def __init__(objeto, reference_frequency, filter_cutoff, output_sample_rate):
        objeto.reference_frequency = reference_frequency
        objeto.filter_cutoff = filter_cutoff
        objeto.output_sample_rate = output_sample_rate

    def process(objeto, t_raw, v_raw):
       
        fs = 1 / (t_raw[1] - t_raw[0])

        
        seno = np.sin(2 * np.pi * objeto.reference_frequency * t_raw)
        coseno = np.cos(2 * np.pi * objeto.reference_frequency * t_raw)
        X = v_raw * seno
        Y = v_raw * coseno

        # Filtro paso bajo 
        sos = signal.butter(4, objeto.filter_cutoff, btype="low", fs=fs, output="sos")
        x_filtrado = signal.sosfilt(sos, X)
        y_filtrado = signal.sosfilt(sos, Y)
        dc_filtrado = signal.sosfilt(sos, v_raw)    # sin mezclar, sin factor 2

        # Decimacion: una muestra de cada N
        N = round(fs / objeto.output_sample_rate)
        t = t_raw[::N]
        x = 2 * x_filtrado[::N]     # 2 * A/2 cos (theta)
        y = 2 * y_filtrado[::N]
        dc = dc_filtrado[::N]

        R = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)

        return {"t": t, "x": x, "y": y, "r": R, "theta": theta, "dc": dc}
