# Vocoder Based on Signoidal Noise Attenuation
based on paper:

*Hu, Y., Loizou, P. C., Li, N., et al. (2007). Use of a sigmoidal-shaped function
for noise attenuation in cochlear implants. J Acoust Soc Am, 122,
128–134.*

#### From the abstact:
*“A new noise reduction algorithm is proposed for cochlear implants
that applies attenuation to the noisy envelopes inversely proportional
to the estimated signal-to-noise ratio (SNR) in each channel […]. Results indicate
that the sigmoidal-shaped weighting function produces significant improvements
to speech recognition compared to the subjects’ daily strategy.
Much of the success of the proposed noise reduction algorithm is attributed
to the improved temporal envelope contrast”*
___
### Vocoder Overview (image taken from paper):
![image](https://user-images.githubusercontent.com/79848589/189127838-3cdae8ca-8ada-4d71-94db-b5c218dd4fd4.png)
___
### Vocoder steps:
#### Step 1:
The noisy speech signal is bandpass filtered into 16 channels 
#### Step 2:
The envelopes are detected in each channel after full-wave rectification and low-pass filtering (200 Hz, sixth-order Butterworth).
#### Step 3:
 The noisy envelopes in each channel are multiplied by channel-specific weighting functions taking values in
the range of zero to one depending on the estimated SNR of that channel.
- Weighing function:
A weighting function that applies heavy attenuation in channels with low SNR and little or no attenuation in channels with high SNR.
The following sigmoidal-shaped function was used: $g(i,l)=e^-β/ξ(i ,l)$
Where β =2, g(i , l) is the weighting function (0<g(i , l)<1), and ξ(i , l) denotes the estimated
instantaneous SNR in the ith channel at stimulation cycle l. This weighting function plateaus at
one for SNR>20 dB and floors to 0 for SNR<−5 dB. The above function was chosen as it has
a sigmoidal shape similar to the human listener’s psychometric function of intelligibility versus
SNR. Other functions with similar shape could alternatively be used.

- SNR estimation:
The computation of the weighting function depends on the estimation of the instantaneous SNR (i , l) of channel i at cycle l: 
![image](https://user-images.githubusercontent.com/79848589/189133952-a86cfdfa-62c7-4071-853a-82775d55fa31.png)
where xˆ(i , l−1) is the enhanced signal envelope obtained in the last stimulation cycle, e is a
small constant 10^-6 needed to avoid possible division by zero in the weights equation, nˆ (i , l) is the estimated envelope amplitude of the noise obtained using a noise-tracking algorithm, α is a smoothing parameter (α = 0.4,0.6 were used and compared) and:
 $γ(i ,l) =y^2 (i ,l)/n^2  (i ,l)$
 
 - Noise tracking algorithm (Cohen and Berdugo, 2002):
 Currently replaced with the noise envelope
 
 - Enhanced envelope:
 Following the weighting function computation, the enhanced temporal envelope is obtained by:
 $ x ̂(i,l)=g(i,l)∙y(i,l) $

where y(i , l) is the noisy envelope of the ith channel at cycle l and xˆ(i , l) contains the enhanced signal envelope.

#### Step 4:
The envelopes attenuated by the channel weighting functions are smoothed with a low-pass filter (200 Hz) and log compressed to the subject’s electrical dynamic range. 

____

### Data Analysis:
#### Envelope detection - rectification + LPF Vs. Hilbert transform
In the paper, the envelope is detected by using rectification + LPF. I decided to go with Hilbert envelope detection because it’s more versatile and doesn’t require choosing a frequency for the LPF, unlike in the rectification method.

#### Explanation about both methods - sited from:
*Marcelo Freitas Caetano, Xavier Rodet. Improved Estimation of the Amplitude Envelope of Time Domain Signals Using True Envelope Cepstral Smoothing.. IEEE International Conference on Acoustics,
Speech and Signal Processing, May 2011, Czech Republic. pp.11-21. ffhal-00604385f*

**Rectification (abs) + LPF**: 
> Low-pass filtering is the most straightforward way of obtaining a smooth signal that follows the amplitude evolution of the original waveform. It is based on a classical amplitude demodulation envelope follower technique, that low-pass filters a half-wave (hwr) or full-wave rectified (fwr) version of an amplitude modulated (AM) signal. The principle of amplitude modulation (AM) is that the amplitude changes of the signal carry the information we seek [...]. Also, the cut-off frequency of the filter has a major impact on the result. High cut-off frequencies will likely produce an amplitude envelope with ripples and very low cut-off frequencies are less responsive to sudden amplitude changes.

**Hilbert envelope detection**: 

The Hilbert transform is part of a signal processing technique for amplitude demodulation. The Hilbert transform of a signal x(t) is defined as
 
where * stands for convolution. Using equation (2), we can define the analytic signal z(t) as 
 
The analytic signal is useful for envelope detection since its modulus r(t) and time derivative of the phase θ(t) can serve as estimates for the amplitude envelope and instantaneous frequency of x(t) under certain conditions. Notably, if the Hilbert transform of x(t) is equal to its quadrature signal [1], then the estimates are equal to the actual information signals [1]. Synthetic (i.e., AM) signals can be constructed to have this property, but there is no reason to expect that acoustic musical instrument sounds or speech also present it. A more realistic condition is verified when we are dealing with narrowband signals [14], which is rarely the case for musical instrument sounds and speech. The analytic signal can be effectively used to extract the amplitude envelope of individual partials if applied to each frequency bin of the STFT, but when applied to the whole signal it is equivalent to trying to demodulate several AM signals at the same time, so we use it as half-wave rectifier in this work.

