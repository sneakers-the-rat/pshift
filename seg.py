import os
import numpy as np
from scipy.io import wavfile
from matplotlib import pyplot as plt
from itertools import product
from PySide import QtCore, QtGui

from pyAudioAnalysis import audioSegmentation as aS

def segment_audio(audio, fs, expansion=0.03, plot=False):

    segments = aS.silenceRemoval(audio, fs, 0.05, 0.01, smoothWindow=0.05, weight=0.15)
    segments = np.row_stack(segments)

    # expand segments
    segments[:,0] -= expansion
    segments[:,1] += expansion

    if plot:
        timeX = np.arange(0, audio.shape[0] / float(fs), 1.0 / fs)
        plt.plot(timeX[:-1], audio)
        for s in segments:
            plt.axvline(x=s[0])
            plt.axvline(x=s[1])

        plt.show()

    return segments

