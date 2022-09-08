# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 14:16:58 2022

@author: micha
"""

# step 1: create noisy signal by adding speech and noise together
import scipy
import librosa
from scipy.io import wavfile
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.io.wavfile import write
from utils import *
import pdb

# load wav files
speech, sr = librosa.load('clean.wav')
additive_noise, sr = librosa.load('noisy_white_3dB.wav')

# test

# create noise
mean = 0
std = 1
num_samples = len(speech)
additive_noise = np.random.uniform(low=0.0, high=0.015, size=len(speech))

# add together
noisy_sig = speech + additive_noise

# TODO: remove
# noisy_sig = noisy_sig[:1000]
channels = 1
f1 = 250
f2 = 8000
order = 256

# create channels
channels_sig = create_channels(channels, f1, f2, sr, order, noisy_sig)
noisy_envelope = env_detect(channels_sig)

# remove zeros from beginning - maybe change the lpf delay
# TODO: remove?
noisy_envelope = noisy_envelope[1000:, :]
# transpose to fit equations from paper
noisy_envelope = np.transpose(noisy_envelope)

# create noise envelope
noise_track_channels = create_channels(channels, f1, f2, sr, order, additive_noise)
noise_track_env = env_detect(noise_track_channels)
noise_track_env = noise_track_env[1000:, :]
# TODO: remove
# n = n[:1000]
noise_track_env = noise_track_env.transpose()

x_after_weights = np.zeros([channels, np.size(noisy_envelope, 1)])
weights = np.zeros([channels, np.size(noisy_envelope, 1)])
xi_vals = np.zeros([channels, np.size(noisy_envelope, 1)])
gamma_vals = np.zeros([channels, np.size(noisy_envelope, 1)])

for i in range(0, channels):
    # first iteration: l = 0
    prev_x = noisy_envelope[i, 0]
    prev_n = noise_track_env[i, 0]
    # TODO: ask about n:
    n = noise_track_env[i, 0]
    y = noisy_envelope[i, 0]
    xi, gamma = estimated_instantaneous_snr(prev_x, i, y, prev_n, n)
    g = weighing_function(xi)
    x = enhanced_signal_envelope(g, y)

    for l in range(1, np.size(noisy_envelope, 1)):
        # update iteration
        prev_x = x
        prev_n = n
        n = noise_track_env[i, l]
        y = noisy_envelope[i, l]
        xi, gamma = estimated_instantaneous_snr(prev_x, i, y, prev_n, n)

        g = weighing_function(xi)
        x = enhanced_signal_envelope(g, y)

        x_after_weights[i, l] = x

        # save values for testing
        weights[i, l] = g
        xi_vals[i, l] = xi
        gamma_vals[i, l] = gamma

lpf_x = np.zeros([channels, np.size(x_after_weights, 1)])

for i in range(0, channels):
    lpf_x[i, :] = butterworth_filter(filter_freq=200,
                                     sr=sr,
                                     filter_order=256,
                                     filter_type='low',
                                     sig_to_filter=x_after_weights[i, :]
                                     )
"""""
from scipy import fftpack

x = x_after_weights.flatten()
# x = noisy_sig
f_s = 22050
X = fftpack.fft(x)
freqs = fftpack.fftfreq(len(x)) * f_s

fig, ax = plt.subplots()

plt.plot(freqs, np.abs(X))
"""""
# reconstruct to 1D array

final_signal = np.sum(lpf_x, axis=0)
plt.plot(final_signal)
a=3