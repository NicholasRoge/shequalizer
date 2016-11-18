import AudioStream

from mmap import mmap
from struct import unpack, calcsize


class WavAudioFile(AudioStream):
    def __init__(self, path, mode = 'rb'):
        self.__file = open(path, mode)
        self.__chunks = {}

        assert(self.__file.read(4) == "RIFF")
        self.__file.read(4)
        assert(self.__file.read(4) == "WAVE")
        
        self._openChunks()

    def _closeChunks(self):
        for chunk_id, chunk in self.__chunks.iteritems():
            chunk.data.close()

        self.__chunks = {}

    def _openChunks(self):
        self._closeChunkMaps()
        
        fileno = self.__file.fileno()

        self.__file.seek(12)
        while True:
            header = self.__file.read(8)
            if header == "":
                break

            header = unpack("4sI", header)
            
            chunk["id"]     = header[0].strip()
            chunk["size"]   = header[1]
            chunk["offset"] = self.__file.tell()
            chunk["cache"]  = {}
            chunk["data"]   = mmap(fileno, chunk["size"], offset = chunk["offset"])
            self.__chunks[chunk["id"]] = chunk
            
            self.__file.seek(chunk["offset"] + chunk["size"])

    def _chunk(self, chunk_id, offset, format):
        if chunk_id not in self.__chunk:
            return None

        chunk = self.__chunk[chunk_id]

        key = (offset, format)
        if key not in chunk["cache"]:
            size = calcsize(format)
            value = unpack(format, chunk[offset:offset + size])

        return chunk["cache"][key]

    @property
    def sampleRate(self):
        return self._chunk("fmt", 4, "I")

    @property
    def sampleWidth(self):
        return self._chunk("fmt", 12, "H")

    @property
    def sampleCount(self):
        return self.__chunks["data"]["size"] / self.sampleWidth

    @property
    def channelWidth(self):
        return self.sampleWidth / self.channelCount

    @property
    def channelCount(self):
        return self._chunk("fmt", 2, "H")

    def seek(self, offset):
        self.__chunk["data"]["data"].seek(self.sampleWidth * offset)

    def readSample(self):
        

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

