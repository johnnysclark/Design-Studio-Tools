"""Auralize a room before it's built: image-source RIR, RT60, and convolution.

Two contrasting shoebox rooms (small absorptive vs large hard hall).
"""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
import pyroomacoustics as pra
from scipy.io import wavfile

FS = 16000
HERE = "/home/user/Design-Studio-Tools/experiments/05_acoustics/"

# name, dims [Lx,Ly,Lz], wall absorption, max_order, src, mic
ROOMS = {
    "small": dict(dims=[4.0, 3.0, 2.6], absorption=0.45, max_order=15,
                  src=[1.0, 1.0, 1.3], mic=[3.0, 2.0, 1.3]),
    "hall":  dict(dims=[30.0, 20.0, 12.0], absorption=0.04, max_order=40,
                  src=[5.0, 5.0, 1.7], mic=[22.0, 15.0, 1.7]),
}

def build_rir(cfg):
    mats = pra.Material(cfg["absorption"])
    room = pra.ShoeBox(cfg["dims"], fs=FS, materials=mats,
                       max_order=cfg["max_order"])
    room.add_source(cfg["src"])
    room.add_microphone(np.array(cfg["mic"]).reshape(3, 1))
    room.compute_rir()
    rir = room.rir[0][0]
    rt60 = room.measure_rt60()[0, 0]
    return rir, rt60

results = {}
for name, cfg in ROOMS.items():
    rir, rt60 = build_rir(cfg)
    results[name] = dict(rir=rir, rt60=rt60, cfg=cfg)
    print(f"[{name:5s}] dims={cfg['dims']} m  absorption={cfg['absorption']:.2f}"
          f"  -> RT60 = {rt60:.3f} s")

# --- compare RIRs ---
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=False)
for ax, name in zip(axes, ROOMS):
    r = results[name]["rir"]
    t = np.arange(len(r)) / FS
    ax.plot(t, r, lw=0.5)
    ax.set_title(f"{name}  (RT60={results[name]['rt60']:.2f}s, "
                 f"abs={ROOMS[name]['absorption']})")
    ax.set_xlabel("time [s]"); ax.set_ylabel("amplitude")
fig.tight_layout(); fig.savefig(HERE + "rir.png", dpi=110)
print("wrote rir.png")

# --- auralize: dry handclap-like white-noise burst with fast decay ---
rng = np.random.default_rng(0)
n = int(0.04 * FS)
dry = (rng.standard_normal(n) * np.exp(-np.linspace(0, 12, n))).astype(np.float64)

def to_int16(x):
    x = x / (np.max(np.abs(x)) + 1e-12)
    return (x * 0.95 * 32767).astype(np.int16)

wavfile.write(HERE + "dry_clap.wav", FS, to_int16(dry))
for name in ROOMS:
    wet = np.convolve(dry, results[name]["rir"])
    fn = HERE + f"auralized_{name}.wav"
    wavfile.write(fn, FS, to_int16(wet))
    print(f"wrote {fn.split('/')[-1]}  dur={len(wet)/FS:.2f}s")

print(f"RT60 contrast: hall/small = "
      f"{results['hall']['rt60']/results['small']['rt60']:.1f}x")
