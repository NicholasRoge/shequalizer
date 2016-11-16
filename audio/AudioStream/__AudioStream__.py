class AudioStream(object):
    @property
    def sampleRate(self):
        raise NotImplementedError()

    @property
    def sampleWidth(self):
        raise NotImplementedError()

    @property
    def sampleCount(self):
        raise NotImplementedError()

    @property
    def channelWidth(self):
        raise NotImplementedError()

    @property
    def channelCount(self):
        raise NotImplementedError()

    def seek(self, offset):
        raise NotImplementedError()

    def readSample(self):
        raise NotImplementedError()

    def readSamples(self, count):
        for i in xrange(count):
            sample = self.readSample()
            if sample == None:
                break
            else:
                yield sample

    def writeSample(self, sample):
        raise NotImplementedError()

    def writeSamples(self, samples, count = None):
        for sample in samples:
            self.writeSample(sample)


