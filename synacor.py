import struct


class CPU():
    def __init__(self, bin_file):
        self.mem = [0] * (1 << 15)
        self.stack = []
        self.reg = [0] * 8
        self.load_bin(bin_file)
        self.codeptr = 0
        self.set_opcodes()

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

    def set_opcodes(self):
        self.opcodes = {
            # 1: (self.sett, 2),
            # 2: (self.push, 1),
            # 3: (self.pop, 1),
            # 4: (self.eq, 3),
            # 5: (self.gt, 3),
            # 6: (self.jmp, 1),
            # 7: (self.jt, 2),
            # 8: (self.jf, 2),
            # 9: (self.add, 3),
            # 10: (self.mult, 3),
            # 11: (self.mod, 3),
            # 12: (self.andd, 3),
            # 13: (self.orr, 3),
            # 14: (self.nott, 2),
            # 15: (self.rmem, 2),
            # 16: (self.wmem, 2),
            # 17: (self.call, 1),
            # 18: (self.ret, 0),
            19: (self.out, 1),
            # 20: (self.inn, 1),
            21: (self.noop, 0)
        }

    def out(self, a):
        print(chr(a), end="")

    def noop(self):
        return

    def bump(self):
        opcode = self.mem[self.codeptr]
        self.codeptr += 1
        return opcode

    def eval(self, opcode):
        (func, nargs) = self.opcodes[opcode]
        args = []
        for _ in range(nargs):
            args.append(self.bump())
        func(*args)

    def run(self):
        while True:
            opcode = self.bump()
            if opcode == 0:     # Shortcircuit 'halt' opcode
                break
            self.eval(opcode)



def main():
    cpu = CPU("challenge.bin")
    cpu.run()


if __name__ == "__main__":
    main()
