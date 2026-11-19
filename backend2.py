
import numpy as np

DC_OFFSET = 0.5
MODULATION_FREQUENCY = 5.0
NOISE_STD = 2.0
PHASE = np.deg2rad(30)    # fase φ de la señal (30 grados, en radianes)

class SimulatedBackend:
    def __init__(objeto, raw_sample_rate, reference_frequency):
        objeto.raw_sample_rate = raw_sample_rate
        objeto.reference_frequency = reference_frequency

    def generate_data(objeto, duration):

        t = np.arange(0, duration, 1 / objeto.raw_sample_rate)
        A = objeto.envelope(t)
        v = A * np.sin(2 * np.pi * objeto.reference_frequency * t + PHASE) + DC_OFFSET + NOISE_STD*np.random.randn(len(t))

        return t, v

    def envelope(objeto, t):
        A = 1 + 0.5 * np.sin(2 * np.pi * MODULATION_FREQUENCY * t)
        return  A 
