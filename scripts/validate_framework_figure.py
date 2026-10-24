"""Fail-closed static geometry/semantics QA for the camera-ready SVG figure.

This does not replace visual proofing, but enforces the *actual arrows*
instead of merely searching figure captions for expected words.
"""
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FIGURE = ROOT / "docs" / "figures" / "ucode-framework.svg"
NS = {"s": "http://www.w3.org/2000/svg"}
FORBIDDEN = ("<script", "foreignObject", "http://", "data:image/", "onload=")


def validate_framework_svg(path: Path = FIGURE) -> dict[str, int]:
    data = path.read_text(encoding="utf-8")
    if any(token in data for token in FORBIDDEN):
        raise ValueError("figure may not embed scripts, foreign objects or external assets")
    root = ET.fromstring(data)
    if root.attrib.get("viewBox") != "0 0 1600 960":
        raise ValueError("unexpected camera-ready SVG geometry")
    if not root.attrib.get("role") == "img":
        raise ValueError("figure missing accessibility role")

    ids = {}
    for node in root.iter():
        if "id" in node.attrib:
            if node.attrib["id"] in ids:
                raise ValueError("duplicate SVG element ID")
            ids[node.attrib["id"]] = node

    required = {
        *(f"policy-flow-{i}-{i+1}" for i in range(1, 6)),
        "evaluation-flow-A-B", "evaluation-flow-B-C", "evaluation-flow-C-D",
        "execution-to-BES-feedback", "task-to-admission",
        "release-to-evaluator", "ttl", "desc",
    }
    if not required.issubset(ids):
        raise ValueError("missing required directional flow or accessible labels")

    policy_x = [25, 285, 545, 805, 1065, 1325]
    for i in range(1, 6):
        arrow = ids[f"policy-flow-{i}-{i+1}"]
        m = re.fullmatch(r"M(\d+) 320 H(\d+)", arrow.attrib.get("d", ""))
        if not m:
            raise ValueError("stage flow must be a straight rightward arrow")
        x1, x2 = map(int, m.groups())
        if not (policy_x[i-1]+240 <= x1 < x2 < policy_x[i]):
            raise ValueError("policy arrow is reversed, misplaced or crosses boxes")
        if arrow.attrib.get("data-from") != str(i):
            raise ValueError("policy edge has wrong source stage")
        if arrow.attrib.get("data-to") != str(i+1):
            raise ValueError("policy edge has wrong destination stage")
        if "marker-end" not in arrow.attrib:
            raise ValueError("policy edge lacks arrowhead")

    for start, end in (("A", "B"), ("B", "C"), ("C", "D")):
        arrow = ids[f"evaluation-flow-{start}-{end}"]
        m = re.fullmatch(r"M(\d+) 796 H(\d+)", arrow.attrib.get("d", ""))
        if not m or int(m.group(1)) >= int(m.group(2)):
            raise ValueError("evaluation arrow is reversed or misaligned")
        if "marker-end" not in arrow.attrib:
            raise ValueError("evaluation flow must point left-to-right")

    feedback = ids["execution-to-BES-feedback"].attrib.get("d", "")
    if "M1185 516 V552" not in feedback or "H943" not in feedback or not feedback.endswith("V517"):
        raise ValueError("feedback must return from stage 5 below stage 4")
    if ids["task-to-admission"].attrib.get("d") != "M145 514 V683":
        raise ValueError("task admission arrow must originate from task input")
    if "M1446 514 V601 H603 V683" not in ids["release-to-evaluator"].attrib.get("d", ""):
        raise ValueError("terminal patch must route to sealed evaluator, not policy")

    visible_text = " ".join((x.text or "") for x in root.iter() if x.tag.endswith("text"))
    for term in ("Bounded Evidence Search", "Independent evaluation", "No held-out labels",
                 "Five-part resource budget", "Risk-gated", "replan under budget"):
        if term not in visible_text:
            raise ValueError(f"figure missing scientific label: {term}")

    return {"policy_edges": 5, "evaluation_edges": 3,
            "feedback_edges": 1, "cross_lane_edges": 2}


def main() -> None:
    report = validate_framework_svg()
    print("FRAMEWORK_SVG_FLOW_QA=PASS " +
          " ".join(f"{k}={v}" for k, v in sorted(report.items())))


if __name__ == "__main__":
    main()
