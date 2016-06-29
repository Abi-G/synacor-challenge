import struct


class CPU():
    def __init__(self, bin):
        self.bin_file = bin
        self.mem = [0] * (1 << 15)
        self.load_bin(self.bin_file)

    def load_bin(self, bin_file):
        f = open(bin_file, "rb")
        ix = 0
        while True:
            v = f.read(2)
            if not v:
                break
            (num,) = struct.unpack("<H", v)
            self.mem[ix] = num
            ix += 1
            print(ix)
