"""Serial vision: Claude Fable 5 narrates the felt experience of MOVING through space.

Thread 16: Simulating experience & time (Kind C -- a model as a design participant).
Gordon Cullen's Townscape argued that architectural meaning is cinematic -- it lives in
the SEQUENCE of revelations, compressions and releases as a body moves, not in any single
view. That is a temporal, experiential reading no static analysis produces.

This tool feeds Fable 5 a circulation path sampled as stations, each carrying an isovist
area (visible floor area in m^2 -- the openness signal that experiments/07_isovist computes
from real geometry) plus a one-word spatial tag, and asks for the serial-vision sequence:
what the moving body feels at each station RELATIVE TO THE ONE BEFORE (the delta is the
content), using the isovist jumps as evidence, ending with where the sequence misfires.

This is the natural successor to thread 07's open question ("serial-vision sequences along
a path") and to thread 14's critic: 14 judges a plan at a moment, 16 simulates it over time.

Model contract (Claude Fable 5): omit `thinking`, steer with output_config.effort, no
sampling params/prefill, check stop_reason == "refusal".

Run:  export ANTHROPIC_API_KEY=sk-ant-... ; pip install anthropic ; python serial_vision.py
"""

# A path through a small civic building. In production these isovist areas come straight
# from experiments/07_isovist run on the real plan polygon; here they are a clean example.
PATH = [
    (1, "Entry vestibule",        24,  "threshold"),
    (2, "Turn into low corridor", 31,  "compression"),
    (3, "Corridor midpoint",      29,  "corridor"),
    (4, "Edge of main hall",      210, "release"),
    (5, "Centre of main hall",    240, "expanse"),
    (6, "Under mezzanine edge",   86,  "shelter"),
    (7, "Stair landing, turning", 120, "pivot"),
    (8, "Reading room doorway",   64,  "arrival"),
]


def path_table(path) -> str:
    return "\n".join(
        f"{i}. {name:24s} isovist {iso:>4} m^2   tag: {tag}"
        for i, name, iso, tag in path)


PROMPT = """You are generating a SERIAL VISION sequence in the tradition of Gordon Cullen's \
Townscape -- the felt, cinematic experience of moving along a path, where meaning comes \
from the unfolding sequence of revelations, compressions and releases, not any single view.

A visitor walks station 1 -> {n}. At each station: the isovist area (visible floor area in \
m^2, a proxy for visual openness) and a one-word spatial tag:

{table}

Write the sequence as {n} short numbered beats (<=45 words each). Each beat names what the \
moving body FEELS at that station and -- crucially -- how it feels RELATIVE TO THE STATION \
BEFORE (the delta is the content: the held breath before release, the over-bright shock \
after the dark corridor, the instinct to pause under the mezzanine). Use the isovist jumps \
as your evidence. After the beats, add one sentence: where the sequence MISFIRES or could \
be sharpened, as a designer's note."""


def serial_vision(path) -> str:
    import anthropic
    client = anthropic.Anthropic()
    prompt = PROMPT.format(n=len(path), table=path_table(path))
    resp = client.messages.create(
        model="claude-fable-5",
        max_tokens=2000,
        output_config={"effort": "high"},
        messages=[{"role": "user", "content": prompt}],
    )
    if resp.stop_reason == "refusal":
        return "[Fable declined this request: " + str(resp.stop_details) + "]"
    return "".join(b.text for b in resp.content if b.type == "text")


if __name__ == "__main__":
    print("Circulation path (isovist areas would come from thread 07 on a real plan):\n")
    print(path_table(PATH))
    print("\n--- Fable 5 serial-vision sequence ---\n")
    try:
        print(serial_vision(PATH))
    except Exception as e:
        print(f"[Could not reach Claude Fable 5: {type(e).__name__}: {e}]")
        print("Set ANTHROPIC_API_KEY and `pip install anthropic` to run live. "
              "A captured Fable 5 transcript is in this folder's README.md.")
