"""Generation half of thread 15: vague brief -> structured spatial program via Claude Fable 5.

Emits a JSON program that program_to_proof.py feeds to z3. Run this with your own key to
regenerate the program for any brief; the proof step uses the captured fable_program.json
so it reproduces offline.

Model contract (Claude Fable 5, see the claude-api skill): omit `thinking` (always-on),
steer with output_config.effort, no sampling params, no prefill, check stop_reason. Fable
does not support assistant prefill, so we ask for a fenced JSON block and parse it.

Run:  export ANTHROPIC_API_KEY=sk-ant-... ; pip install anthropic ; python fable_program_gen.py
"""
import json
import re
import sys

BRIEF = (
    "We want to add a small step-free annex in the back garden for my elderly mother. "
    "She needs her own bedroom, a proper bathroom she can use with a walker, a little "
    "kitchenette, and a sunny sitting area where she reads in the mornings. Keep it cosy "
    "but not cramped. The garden footprint we can give it is about 8 metres wide by 6 "
    "metres deep."
)

PROMPT = """You are a programming/briefing assistant for an architect. Convert the client \
brief into a STRUCTURED SPATIAL PROGRAM a constraint solver can consume.

CLIENT BRIEF (verbatim, vague on purpose):
"{brief}"

Produce ONLY a single JSON object inside one ```json fenced code block, no prose outside it:

{{
  "envelope": {{"width": <m>, "depth": <m>}},
  "rooms": [
    {{"name": "<str>", "min_w": <m>, "min_d": <m>, "needs_window": [<subset of "N","E","S","W">], "function": "<habitable|service|circulation>", "occupancy": <int>}}
  ],
  "adjacencies": [["<roomA>","<roomB>"], ...],
  "rationale": "<=60 words on the key decisions you INFERRED from the vague brief"
}}

Rules: metres, 0.5 steps, rectangular rooms, dimensions are MINIMUM clear sizes. Infer \
accessibility (walker => generous bathroom; step-free => single level + wide hall) and \
morning-light needs (sitting area faces E or S) and turn them into concrete numbers. \
4-6 rooms incl. any circulation. Envelope from the brief. Output JSON only."""


def generate(brief: str) -> dict:
    import anthropic
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-fable-5",
        max_tokens=2000,
        output_config={"effort": "medium"},   # structured extraction; medium is plenty
        messages=[{"role": "user", "content": PROMPT.format(brief=brief)}],
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError(f"Fable declined: {resp.stop_details}")
    text = "".join(b.text for b in resp.content if b.type == "text")
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S) or re.search(r"(\{.*\})", text, re.S)
    if not m:
        raise ValueError("no JSON object found in Fable's response:\n" + text)
    return json.loads(m.group(1))


if __name__ == "__main__":
    try:
        program = generate(BRIEF)
    except Exception as e:
        print(f"[Could not reach Claude Fable 5: {type(e).__name__}: {e}]", file=sys.stderr)
        print("Set ANTHROPIC_API_KEY and `pip install anthropic`. The program Fable produced "
              "for this brief is captured in fable_program.json; program_to_proof.py uses it.",
              file=sys.stderr)
        sys.exit(1)
    print(json.dumps(program, indent=2))
