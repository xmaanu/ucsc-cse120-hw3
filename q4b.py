import pyrtl

if __name__ == "__main__":
    enable = pyrtl.Input(1, "enable")
    reset = pyrtl.Input(1, "reset")
    y = pyrtl.Register(2, "y")

    # reset = 1           -> y <- 0           (enable is don't care)
    # reset = 0, enable=0 -> y <- y           (hold)
    # reset = 0, enable=1 -> y <- y + 1       (wraps around because y is 2 bits)
    hold_or_inc = pyrtl.select(enable, truecase=(y + 1)[:2], falsecase=y)
    y.next <<= pyrtl.select(reset, truecase=pyrtl.Const(0, bitwidth=2), falsecase=hold_or_inc)

    trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=trace)
    sim.step({"reset": 1, "enable": 0})   # reset -> y = 0 next cycle
    sim.step({"reset": 0, "enable": 1})   # count
    sim.step({"reset": 0, "enable": 1})   # count
    sim.step({"reset": 0, "enable": 1})   # count
    sim.step({"reset": 0, "enable": 0})   # hold
    sim.step({"reset": 0, "enable": 0})   # hold
    sim.step({"reset": 0, "enable": 1})   # count (wraps 3 -> 0)
    sim.step({"reset": 0, "enable": 1})   # count
    sim.step({"reset": 1, "enable": 1})   # reset wins over enable
    sim.step({"reset": 0, "enable": 1})   # count again from 0
    sim.step({"reset": 0, "enable": 0})   # hold

    trace.render_trace()
