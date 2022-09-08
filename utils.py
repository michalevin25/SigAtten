import scipy
import librosa
from scipy.io import wavfile
from scipy import signal
from scipy.signal import hilbert
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.io.wavfile import write


def create_channels(channels, f1, f2, sr, order, current_signal):
    # create channels using band pass filter and logarithmic center frequencies

    # for info on frequencies:
    center_f = np.logspace(np.log10(f1), np.log10(f2), num=channels)

    # halfwidth & edge frequencies
    halfwidth = np.log2(f2 / f1) / (2 * channels)
    frequency = f1 * np.power(2, range(1, 2 * channels, 2) * halfwidth)
    bandwidth = 2 * halfwidth

    channels_sig = np.zeros([len(current_signal), channels])
    for ii in range(0, channels):
        A = np.power(2, (-bandwidth / 2))
        B = np.power(2, (bandwidth / 2))
        Edge = frequency[ii] * np.array([A, B])
        Edge = 2 * Edge / sr
        Edge[1] = min(0.99, Edge[1])
        hann_win = signal.firwin(order + 1, Edge, window="hann")
        channels_sig[:, ii] = signal.lfilter(hann_win, 1, current_signal)
    return channels_sig


def butterworth_filter(filter_freq, sr, filter_order, filter_type, sig_to_filter):
    filter_freq = filter_freq   # normalized freq for filter
    b, a = signal.butter(filter_order, filter_freq, filter_type)  # consturct lpf butterworth filter
    lpf_sig = signal.filtfilt(b, a, sig_to_filter, axis=0)  # apply filter to signal
    return lpf_sig




"""""
def env_detect(sig, filter_order, filter_freq, sr):
    # envelope detection - full wave rectification + LPF
    # rectification:
    wave_rect_sig = np.absolute(sig)
    # low pass filter:
    filter_type = 'low'
    envelope = butterworth_filter(filter_freq, sr, filter_order, filter_type, wave_rect_sig)
    return envelope


"""""
def env_detect(sig):
    # envelope detection - absolute value of hilbert
    envelope = np.absolute(hilbert(sig))

    return envelope

##### weighing equations #####
def noise_env_amp(additive_noise):
    n = env_detect(additive_noise, filter_order=6, filter_freq=200, sr=sr)
    return n


def gamma_calc(y, n):
    gamma = (y ** 2) / (n ** 2)

    return gamma


def estimated_instantaneous_snr(prev_x, i, y, prev_n, n):
    alpha = 0.4  # smoothing constant
    # TODO: compare to alpha = 0.6
    epsilon = 10 ** -6  # small constant needed to avoid possible division by zero
    gamma = gamma_calc(y, n)
    # TODO: change to gamma-1
    if i <= 10:
        xi = (alpha * (prev_x ** 2) / prev_n ** 2) + (1 - alpha) * max(gamma, 0)
    if i > 10:
        xi = max(gamma - 1, epsilon)
    # TODO: remove return gamma
    return xi, gamma


def weighing_function(xi):
    betta = 2
    g = math.exp(-betta / xi)
    return g


def enhanced_signal_envelope(g, y):
    # noisy envelopes in each channel are multiplied by channel-specific weighting
    # functions taking values in the range of zero to one
    # depending on the estimated SNR of that channel

    # y[i,l] is the noisy envelope of the ith channel at cycle l
    x = g * y
    return x
