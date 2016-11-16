import struct
import sys

from math import ceil


class AudioFile(object):
    def __init__(self, path, mode = "r", buffering = -1):
        self._file = builtin_open(path, mode + "b", buffering)

    @property
    def duration(self):
        return float(self.sample_count) / float(self.sample_rate)

    @property
    def sample_count(self):
        raise NotImplementedError()

    @property
    def sample_rate(self):
        raise NotImplementedError()

    @property
    def channels(self):
        raise NotImplementedError()

    @property
    def channel_bits(self):
        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def close(self):
        return self._file.close()

    def pos(self, sample):
        raise NotImplementedError()

    def begin(self):
        self.pos(0)

    def end(self):
        self.pos(len(self))

    def read(self, count = 1):
        raise NotImplementedError()

    def write(self, samples):
        raise NotImplementedError()

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step == None or key.step == 1:
                self.pos(key.start)
                for sample in self.read(key.stop - key.start):
                    yield sample
            else:
                for offset in xrange(key.start, key.end, key.step):
                    yield self[offset]
        else:
            self.pos(offset)
            yield self.read()

    def __len__(self):
        return self.sample_count

class WavFile(AudioFile):
    def __init__(self, path, mode = "r", buffering = -1):
        super(WavFile, self).__init__(path, mode, buffering)

        self._file.seek(0)
        header = self._file.read(12)
        header = struct.unpack("4sI4s", header)
        assert(header[0] == "RIFF")
        assert(header[2] == "WAVE")

        assert(self._file.read(4) == "fmt ")
        self._file.read(4) #fmt chunk size
        fields = [
            ("format", "h"),        # 0
            ("channel.count", "H"), # 2
            ("sample.rate", "I"),   # 4
            (None, "I"),            # 8
            ("sample.size", "H"),   # 12
            ("sample.bits", "H"),   # 14
        ]

        data_format = "".join((field[1] for field in fields))
        data_size = struct.calcsize(data_format)
        data = self._file.read(data_size)
        data = struct.unpack(data_format, data)
        
        self._format = {}
        for offset in xrange(len(fields)):
            field = fields[offset]
            
            if field[0] == None:
                continue

            self._format[field[0]] = data[offset]

        assert(self._file.read(4) == "data")
        data_size = self._file.read(4)
        data_size = struct.unpack("I", data_size)[0]; 
        self._format["sample.count"] = data_size / self._format["sample.size"]

        channel_size = self._format["sample.size"] / self._format["channel.count"]
        channel_format = ["b", "h", "", "i"][channel_size - 1]
        self._format["channel.format"] = "%i%s" % (self._format["channel.count"], channel_format)

    @property
    def sample_count(self):
        return self._format["sample.count"]

    @property
    def sample_rate(self):
        return self._format["sample.rate"]

    @property
    def channels(self):
        return self._format["channel.count"]

    def pos(self, sample):
        self._file.seek(44 + (sample * self._format["sample.size"]))
    
    def read(self, count = 1):
        while count > 0:
            sample = self._file.read(self._format["sample.size"])
            yield struct.unpack(self._format["channel.format"], sample)

            count -= 1

    def write(self, samples):
        raise NotImplementedError()

builtin_open = open
def open(path, mode = "r", buffering = -1):
    offset = path.rfind(".")
    if offset == -1:
        return None

    extension = path[offset + 1:].lower()
    if extension == "wav":
        return WavFile(path, mode, buffering)
    else:
        raise NotImplementedError()
