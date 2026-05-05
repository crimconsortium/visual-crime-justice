"""Post-process the rendered scenario-pack HTML into semantic, interactive structure.

The Markdown source uses these labelled paragraphs inside each scenario:
  **Situation.** ...
  **Discussion questions.** (followed by <ol>)
  **Model response.** ...
  **Facilitator notes.** ...

This module splits the rendered HTML on <hr/> boundaries, identifies scenario
blocks (those starting with <h2>), and rewraps each labelled paragraph (and the
<ol> after the questions paragraph) into named <div>/<details> blocks so the
browser-side JS can show/hide them by mode.
"""

from __future__ import annotations

import re


_SCENARIO_HEADER_RE = re.compile(r"<h2[^>]*>\s*Scenario\s+\d+", re.IGNORECASE)
_LABEL_RE = re.compile(
    r"<p>\s*<strong>(?P<label>Situation|Discussion questions|Model response|Facilitator notes)\.</strong>\s*(?P<rest>.*?)</p>",
    re.IGNORECASE | re.DOTALL,
)


def _split_on_hr(html: str) -> list[str]:
    """Split HTML into chunks by <hr> tags, keeping order."""
    return re.split(r"<hr\s*/?>", html, flags=re.IGNORECASE)


def _classify_block(label: str) -> str:
    label = label.strip().lower()
    return {
        "situation": "scenario-situation",
        "discussion questions": "scenario-questions",
        "model response": "scenario-response",
        "facilitator notes": "scenario-facilitator",
    }[label]


def _wrap_scenario(chunk: str, idx: int) -> str:
    """Convert one scenario chunk into a semantic <section>."""
    # Find labelled paragraphs and the next sibling block (e.g. <ol>) for questions.
    parts: list[tuple[str, str]] = []  # (block_class, html)
    pieces = list(_LABEL_RE.finditer(chunk))
    if not pieces:
        # No recognised labels — leave chunk alone but still wrap so JS can target it.
        return f'<section class="scenario" data-scenario="{idx}">{chunk}</section>'

    # Pull out the <h2> heading and any preface text before the first label.
    first_start = pieces[0].start()
    head = chunk[:first_start]

    for i, m in enumerate(pieces):
        end = pieces[i + 1].start() if i + 1 < len(pieces) else len(chunk)
        block = chunk[m.start():end]
        cls = _classify_block(m.group("label"))
        # Strip the leading "<p><strong>Label.</strong>" from the paragraph and
        # rebuild as a clean paragraph; keep any trailing siblings (e.g. <ol>).
        rest = m.group("rest").rstrip()
        # Everything after the first </p> belongs alongside the label paragraph
        # (e.g. an <ol> following Discussion questions).
        first_p_end = block.find("</p>")
        trailing = block[first_p_end + len("</p>"):] if first_p_end != -1 else ""
        # If the label paragraph had no inline body (because the list now
        # follows on the next block), drop the empty <p></p> entirely.
        if rest:
            inner = f"<p>{rest}</p>{trailing}".strip()
        else:
            inner = trailing.strip()
        parts.append((cls, inner))

    # Render scenario.
    out = [f'<section class="scenario" data-scenario="{idx}">', head.strip()]
    for cls, inner in parts:
        if cls == "scenario-response":
            out.append(
                f'<details class="scenario-response">'
                f'<summary>Show model response</summary>'
                f'<div class="scenario-response-body">{inner}</div>'
                f'</details>'
            )
        elif cls == "scenario-facilitator":
            out.append(
                f'<details class="scenario-facilitator">'
                f'<summary>Facilitator notes</summary>'
                f'<div class="scenario-facilitator-body">{inner}</div>'
                f'</details>'
            )
        elif cls == "scenario-questions":
            out.append(
                f'<div class="{cls}">{inner}'
                f'<div class="scenario-workbook">'
                f'<label for="workbook-{idx}">Your response (saved to this browser only)</label>'
                f'<textarea id="workbook-{idx}" data-scenario-id="{idx}" rows="6" '
                f'placeholder="Write your reasoning before revealing the model response..."></textarea>'
                f'</div></div>'
            )
        else:
            out.append(f'<div class="{cls}">{inner}</div>')
    out.append("</section>")
    return "\n".join(out)


def process(html: str) -> str:
    """Return the scenario-pack body with each scenario wrapped semantically."""
    chunks = _split_on_hr(html)
    rendered: list[str] = []
    scenario_idx = 0
    for chunk in chunks:
        if _SCENARIO_HEADER_RE.search(chunk):
            scenario_idx += 1
            rendered.append(_wrap_scenario(chunk, scenario_idx))
        else:
            rendered.append(chunk)
    return "<hr/>".join(rendered)
