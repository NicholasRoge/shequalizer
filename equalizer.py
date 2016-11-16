#!/usr/bin/env python2.7

import audio
import numpy as np
import sys

from math import floor
from matplotlib import pyplot


path = sys.argv[1]
with audio.open(path) as file:
    w = np.fft.fft([sample[0] for sample in file[0:file.sample_count]])
    frequencies = np.fft.fftfreq(len(w))
      
    max_offset = np.argmax(np.abs(w))
    max_frequency = frequencies[max_offset]
    hertz = abs(max_frequency * file.sample_rate)
    print("%ihz" % hertz)

    # pyplot.plot(frequencies, antialiased = True, linewidth = 0.5)
    # pyplot.show()
