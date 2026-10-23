import pyrtl

def datapath(zero, lt, opcode):
    # opcode: 00 blt (<), 01 bge (>=), 10 beq (==), 11 bne (!=)
    # opcode[1] picks which ALU signal to look at:  0 -> lt,  1 -> zero
    # opcode[0] says whether the condition is negated (bge = not blt, bne = not beq)
    base = pyrtl.select(opcode[1], truecase=zero, falsecase=lt)
    branch = base ^ opcode[0]
    return branch

if __name__ == "__main__":
    zero = pyrtl.Input(1, "zero")
    lt = pyrtl.Input(1, "lt")
    opcode = pyrtl.Input(2, "opcode")

    branch_out = datapath(zero, lt, opcode)

    branch = pyrtl.Output(1, "branch")
    branch <<= branch_out

    sim = pyrtl.Simulation()

    # Example test case below, this should PASS
    try:
        sim.step({"zero" : 0, "lt" : 1, "opcode": 0})
        assert sim.inspect("branch") == 1
        print("Test PASS")
    except:
        print("Test FAIL")

    # ---- Additional tests: exhaustive over every (opcode, zero, lt) combination ----
    # Legal ALU outputs: if zero=1 then lt=0 (A-B==0 cannot also be A<B), but we test all 8
    # combinations of (zero, lt) anyway so the block is correct for any input.
    expected = {
        0b00: lambda z, l: l,         # blt
        0b01: lambda z, l: 1 - l,     # bge
        0b10: lambda z, l: z,         # beq
        0b11: lambda z, l: 1 - z,     # bne
    }
    names = {0: "blt", 1: "bge", 2: "beq", 3: "bne"}
    failures = 0
    for op in range(4):
        for z in range(2):
            for l in range(2):
                sim.step({"zero": z, "lt": l, "opcode": op})
                got = sim.inspect("branch")
                exp = expected[op](z, l)
                ok = (got == exp)
                failures += (not ok)
                print(f"{names[op]} zero={z} lt={l} -> branch={got} (expected {exp}) {'PASS' if ok else 'FAIL'}")
    print("ALL TESTS PASSED" if failures == 0 else f"{failures} TEST(S) FAILED")
