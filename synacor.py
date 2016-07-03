import struct
import pickle
import argparse

DEBUG = False


class CPU():
    def __init__(self, bin_file):
        self.mem = [0] * (1 << 15)
        self.stack = []
        self.reg = [0] * 8
        self.load_bin(bin_file)
        self.codeptr = 0
        self.set_opcodes()
        self.buffer = ""

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
            1: (self.sett, 2, "w"),
            2: (self.push, 1, "r"),
            3: (self.pop, 1, "w"),
            4: (self.eq, 3, "w"),
            5: (self.gt, 3, "w"),
            6: (self.jmp, 1, "r"),
            7: (self.jt, 2, "r"),
            8: (self.jf, 2, "r"),
            9: (self.add, 3, "w"),
            10: (self.mult, 3, "w"),
            11: (self.mod, 3, "w"),
            12: (self.andd, 3, "w"),
            13: (self.orr, 3, "w"),
            14: (self.nott, 2, "w"),
            15: (self.rmem, 2, "w"),
            16: (self.wmem, 2, "r"),
            17: (self.call, 1, "r"),
            18: (self.ret, 0, "r"),
            19: (self.out, 1, "r"),
            20: (self.inn, 1, "w"),
            21: (self.noop, 0, "r")
        }

        self.opcode_meta = {
            0: ("HALT", 0, "r"),
            1: ("SET", 2, "w"),
            2: ("PUSH", 1, "r"),
            3: ("POP", 1, "w"),
            4: ("EQ", 3, "w"),
            5: ("GT", 3, "w"),
            6: ("JMP", 1, "r"),
            7: ("JT", 2, "r"),
            8: ("JF", 2, "r"),
            9: ("ADD", 3, "w"),
            10: ("MULT", 3, "w"),
            11: ("MOD", 3, "w"),
            12: ("AND", 3, "w"),
            13: ("OR", 3, "w"),
            14: ("NOT", 2, "w"),
            15: ("RMEM", 2, "w"),
            16: ("WMEM", 2, "r"),
            17: ("CALL", 1, "r"),
            18: ("RET", 0, "r"),
            19: ("OUT", 1, "r"),
            20: ("IN", 1, "w"),
            21: ("NOOP", 0, "r")
        }

    def sett(self, a, b):
        self.reg[a] = b

    def push(self, a):
        self.stack.append(a)

    def pop(self, a):
        self.reg[a] = self.stack.pop()

    def eq(self, a, b, c):
        if b == c:
            self.reg[a] = 1
        else:
            self.reg[a] = 0

    def gt(self, a, b, c):
        if b > c:
            self.reg[a] = 1
        else:
            self.reg[a] = 0

    def jmp(self, a):
        self.codeptr = a

    def jt(self, a, b):
        if a != 0:
            self.codeptr = b
        else:
            return

    def jf(self, a, b):
        if a == 0:
            self.codeptr = b
        else:
            return

    def add(self, a, b, c):
        self.reg[a] = (b + c) % 32768

    def mult(self, a, b, c):
        self.reg[a] = (b * c) % 32768

    def mod(self, a, b, c):
        self.reg[a] = b % c

    def andd(self, a, b, c):
        self.reg[a] = b & c

    def orr(self, a, b, c):
        self.reg[a] = b | c

    def nott(self, a, b):
        # See blog for notes
        mask = 0x7fff
        self.reg[a] = ~b & mask

    def rmem(self, a, b):
        self.reg[a] = self.mem[b]

    def wmem(self, a, b):
        self.mem[a] = b

    def call(self, a):
        self.stack.append(self.codeptr)
        self.codeptr = a

    def ret(self):
        self.codeptr = self.stack.pop()

    def out(self, a):
        print(chr(a), end="")

    def inn(self, a):
        if not self.buffer:
            while True:
                print("> ", end="")
                v = input()
                if v == "save":
                    print("To save type 'save <filename>'")
                    continue
                if v.startswith("save "):
                    splt = v.split()
                    if len(splt) == 2:
                        path = splt[1]
                        # Set buffer to "look" so on resume, get useful message
                        self.buffer = "look\n"
                        self.reg[a] = ord(self.buffer[0])
                        self.buffer = self.buffer[1:]
                        self.save(path)
                    else:
                        print("To save type 'save <filename>'")
                else:
                    self.buffer = v + "\n"
                    break
        self.reg[a] = ord(self.buffer[0])
        self.buffer = self.buffer[1:]

    def noop(self):
        return

    def bump(self):
        opcode = self.mem[self.codeptr]
        self.codeptr += 1
        return opcode

    def eval(self, opcode):
        (func, nargs, rw) = self.opcodes[opcode]
        args = []
        for ix in range(nargs):
            arg = self.bump()
            if (32768 <= arg <= 32775):
                arg = arg - 32768
                if not (ix == 0 and rw == "w"):
                    arg = self.reg[arg]
            args.append(arg)
        func(*args)

    def disasm(self):
        while True:
            ptr = self.codeptr
            try:
                opcode = self.bump()
            except IndexError:
                break
            try:
                (instr, nargs, rw) = self.opcode_meta[opcode]
            except KeyError:
                (instr, nargs, rw) = ("UNK", 0, "r")
            args = []
            for ix in range(nargs):
                arg = self.bump()
                if (32768 <= arg <= 32775):
                    arg = arg - 32768
                    if not (ix == 0 and rw == "w"):
                        arg = self.reg[arg]
                args.append(arg)
            print(ptr, instr, args)


    def run(self):
        while True:
            opcode = self.bump()
            dbg_print("ptr2", self.codeptr)
            dbg_print("opcode:", opcode)
            if opcode == 0:     # Shortcircuit 'halt' opcode
                break
            self.eval(opcode)
            dbg_print("ptr3", self.codeptr)

    def display(self):
        print("Pointer at pos %d, val %d: " % (self.codeptr, self.mem[self.codeptr]))
        start = max(0, self.codeptr - 5)
        stop = min(len(self.mem), self.codeptr + 5)
        print("Local memory range: ", self.mem[start:stop])
        print("Registers: ", self.reg)
        print("Stack: ", self.stack)

    def save(self, path):
        pickle.dump(self, open(path, "wb"))
        print("File saved")


def load(filename):
    cpu = pickle.load(open(filename, "rb"))
    return cpu


def dbg_print(*msgs):
    if DEBUG:
        print(*msgs)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", help="load memory state")
    parser.add_argument("--disasm", action="store_true", help="activate disassembler")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.filename:
        cpu = CPU("challenge.bin")
    else:
        cpu = load(args.filename)
    if args.disasm:
        cpu.disasm()
    else:
        cpu.run()


if __name__ == "__main__":
    main()
