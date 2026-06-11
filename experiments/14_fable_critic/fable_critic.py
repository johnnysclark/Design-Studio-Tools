"""The jury before the jury: Claude Fable 5 as an EXPERIENTIAL design critic.

Thread 14: Executable theory / adversarial critic (Kind C -- a model as a design
participant). Pairs with experiments/10_pattern_linter, which deliberately stops at the
structural/topological layer ("critiques structure, never the poetics"). This tool takes
the SAME structured building model plus the offline linter's structural findings, and asks
Fable 5 for the layer the rule engine cannot reach: what it would FEEL like to move through
and inhabit the plan -- light quality over the day, arrival sequence, prospect/refuge,
threshold, the social life of the plan -- ending with the sharpest question a review jury
would ask.

Division of labour:
  offline pattern-linter (thread 10)  ->  PROVABLE structural violations (deterministic, ms)
  Fable 5 critic (this tool)          ->  EXPERIENTIAL judgement (learned, ~30 s)

Model contract (Claude Fable 5, see the claude-api skill): omit `thinking` entirely
(always-on; an explicit disabled errors), steer depth with output_config.effort, no
sampling params, no prefill, and CHECK stop_reason == "refusal" before reading content.

Run (needs your own key -- the headless research container has none):
    export ANTHROPIC_API_KEY=sk-ant-...
    pip install anthropic
    python fable_critic.py
"""
from dataclasses import dataclass, field


# --- a structured building model (same shape as thread 10's Room/Building) ------------ #
@dataclass
class Room:
    name: str
    bbox: tuple                       # (minx, miny, maxx, maxy), metres
    windows: list = field(default_factory=list)   # exterior orientations: N/E/S/W
    function: str = "habitable"
    occupancy: int = 1


@dataclass
class Building:
    rooms: list
    entry: str
    adjacencies: list                 # (roomA, roomB) doored connections


def example_building():
    rooms = [
        Room("Entry",      (0, 0, 2, 2),    ["S"],      "entry"),
        Room("Living",     (2, 0, 7, 4),    ["S", "E"], "habitable", 6),
        Room("Kitchen",    (7, 0, 10, 4),   ["S", "E"], "habitable", 3),
        Room("Hall",       (2, 4, 7, 5.5),  [],         "circulation"),
        Room("Study",      (2, 5.5, 5, 8),  ["N"],      "habitable", 1),
        Room("MasterBed",  (0, 2, 2, 6),    ["W"],      "habitable", 2),
        Room("Bedroom2",   (5, 5.5, 9, 8),  ["N", "E"], "habitable", 2),
        Room("Gallery",    (7, 4, 12, 5),   ["S", "N"], "habitable", 2),
        Room("Garden",     (0, -4, 12, 0),  [],         "outdoor"),
    ]
    adj = [("Entry", "Living"), ("Entry", "MasterBed"), ("Living", "Kitchen"),
           ("Living", "Hall"), ("Kitchen", "Gallery"), ("Hall", "Study"),
           ("Study", "Bedroom2"), ("Living", "Garden")]
    return Building(rooms, "Entry", adj)


# Structural findings handed over by the offline linter (thread 10) -- Fable does NOT
# re-derive these; it builds the experiential layer ON TOP of them.
LINTER_FINDINGS = [
    "MasterBed has light on one side only (#159) and opens directly off the Entry (no intimacy gradient, #127)",
    "Bedroom2 is reachable only through the Study (no flow, #131)",
    "Gallery is 5 m x 1 m -> 5:1 aspect (#109)",
]


def describe(b: Building) -> str:
    lines = ["Single-storey house. Rooms as axis-aligned boxes, metres "
             "(x=0 West, y=0 South):"]
    for r in b.rooms:
        x0, y0, x1, y1 = r.bbox
        w = ", windows: " + "/".join(r.windows) if r.windows else ", no windows"
        occ = f", occ {r.occupancy}" if r.function == "habitable" else ""
        lines.append(f"  {r.name}: ({x0},{y0})-({x1},{y1}) [{r.function}{occ}{w}]")
    lines.append("Entry: " + b.entry)
    lines.append("Doored connections: " + ", ".join(f"{a}-{b_}" for a, b_ in b.adjacencies))
    return "\n".join(lines)


PROMPT = """You are a sharp architectural design critic at a review. Here is a structured \
building model:

{model}

An offline rule-linter has ALREADY flagged these STRUCTURAL violations -- do not just \
restate them:
{findings}

Your job is the EXPERIENTIAL layer the rule-linter cannot reach. In <=250 words: what \
would it FEEL like to move through and inhabit this house? Name 2-3 specific experiential \
failures or opportunities a jury would raise that are NOT restatements of the structural \
flags -- light quality through the day, sequence and arrival, prospect/refuge, threshold, \
the social life of the plan. Be concrete and specific to THIS plan's geometry (cite \
coordinates/dimensions where they drive the point). End with the single sharpest question \
you would ask the designer."""


def critique(building: Building, findings: list[str]) -> str:
    import anthropic
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN
    prompt = PROMPT.format(
        model=describe(building),
        findings="\n".join(f"  - {f}" for f in findings),
    )
    resp = client.messages.create(
        model="claude-fable-5",
        max_tokens=2000,
        output_config={"effort": "high"},   # intelligence-sensitive judgement
        messages=[{"role": "user", "content": prompt}],
    )
    if resp.stop_reason == "refusal":        # Fable 5: always check before reading content
        return "[Fable declined this request: " + str(resp.stop_details) + "]"
    return "".join(b.text for b in resp.content if b.type == "text")


if __name__ == "__main__":
    b = example_building()
    print(describe(b))
    print("\nOffline linter (structural) said:")
    for f in LINTER_FINDINGS:
        print("  -", f)
    print("\n--- Fable 5 experiential critique ---\n")
    try:
        print(critique(b, LINTER_FINDINGS))
    except Exception as e:
        print(f"[Could not reach Claude Fable 5: {type(e).__name__}: {e}]")
        print("Set ANTHROPIC_API_KEY and `pip install anthropic` to run live. "
              "A captured Fable 5 transcript is in this folder's README.md.")
