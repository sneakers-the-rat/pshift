import os
from scipy.io import wavfile
from matplotlib import pyplot as plt


base_dir = '~/speech_recordings'
fn = '/home/lab/speech_recordings/Aldis/Aldis_cv_1.wav'

fs, data = wavfile.read(fn)