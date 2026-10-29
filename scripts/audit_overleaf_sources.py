"""Fail-closed source checks for the U-CODE Springer/Overleaf working manuscript.

This is NOT a LaTeX compilation, publisher-compliance certificate, reference
fact-check, plagiarism check, or a substitute for reviewing the finished PDF.
It catches inspectable source-integrity failures without downloading a
publisher class, connecting to Overleaf, or inventing experimental results.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "paper/overleaf/main.tex"
BIB = ROOT / "paper/overleaf/references.bib"

_CITES = re.compile(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\]\s*){0,2}\{([^{}]+)\}")
_REFS = re.compile(r"\\(?:eqref|ref|autoref|cref|Cref)\{([^{}]+)\}")
_LABEL = re.compile(r"\\label\{([^{}]+)\}")
_BIBKEY = re.compile(r"(?m)@\w+\s*[\{\(]\s*([^,\s{}()]+)\s*,")
_BEGIN_END = re.compile(r"\\(begin|end)\{([A-Za-z*]+)\}")
_KEYWORDS = re.compile(r"\\keywords\{([^{}]+)\}")
_ABSTRACT = re.compile(r"\\abstract\s*\{\s*%\s*(.*?)\n\}", flags=re.DOTALL)


def uncomment(text: str) -> str:
    """Remove comments, but preserve literal LaTeX escaped percentages."""
    return "\n".join(re.sub(r"(?<!\\)%[^\n]*$", "", line)
                     for line in text.splitlines())


COMPARISON_KEYS = (
    "antoniades2025swesearch", "gong2025ga4gc",
    "ding2026swereplay", "zou2026sweverifier",
    "kulkarni2026pats", "li2026retrace", "zeng2026dockerless",
)


def audit_comparison_table(paper: str) -> dict:
    """Keep the comparison descriptive, cited and explicitly pre-empirical.

    Static checks cannot establish the literature characterization, compile
    a publisher PDF or prove real benchmark performance.
    """
    match = re.search(
        r"\\begin\{table\*\}\[t\](.*?)\\end\{table\*\}",
        paper, flags=re.DOTALL)
    if match is None:
        raise ValueError("missing novelty comparison table")
    table = match.group(1)
    if (r"\label{tab:prior-method-positioning}" not in table or
            r"\methodPlan" not in table or
            r"\methodNo" not in table or
            r"\methodYes" not in table):
        raise ValueError("missing novelty table label or explanation of markers")
    for key in COMPARISON_KEYS:
        if r"\cite{"+key+"}" not in table:
            raise ValueError("novelty table missing primary-source citation: "+key)
    # Whitespace may vary; evaluate only the U-CODE row, not nearby paper text.
    row_match = re.search(
        r"\\textbf\{U-CODE \(this study; prospective\)\}" +
        r"(.*?)\\\\", table, flags=re.DOTALL)
    if row_match is None:
        raise ValueError("missing explicit prospective U-CODE table row")
    row = [x.strip() for x in row_match.group(1).split("&")]
    if row != ["", *([r"\methodPlan"] * 5), r"\methodNo"]:
        raise ValueError("U-CODE methods planned and real results absent required")
    for must in ("not a performance", "experimentally validated", "not exhaustive"):
        if must not in table.lower():
            raise ValueError("novelty table lost non-superiority/evidence caveat")
    if re.search(r"\b(?:U-CODE\s+(?:outperforms|surpasses|beats)|"
                 r"best\s+performance|proven\s+superior)\b",
                 table, flags=re.IGNORECASE):
        raise ValueError("unmeasured superiority claim in novelty table")
    return {"sources": len(COMPARISON_KEYS),
            "real_ucode_results": 0,
            "interpretation": "DESCRIPTIVE_METHOD_POSITIONING_ONLY"}


def audit_manuscript(main_text: str, bib_text: str) -> dict:
    if not isinstance(main_text, str) or not isinstance(bib_text, str):
        raise TypeError("the paper and BibTeX must be UTF-8 text")
    paper = uncomment(main_text)
    if not paper.strip() or not bib_text.strip():
        raise ValueError("empty manuscript or bibliography")
    if (not re.search(r"\\documentclass\[[^\]]*\]\{sn-jnl\}", paper)
            or "\\begin{document}" not in paper
            or "\\end{document}" not in paper
            or "\\maketitle" not in paper
            or "\\bibliography{references}" not in paper):
        raise ValueError("missing Springer class, document skeleton or references")
    if re.search(r"\\input\{(?:/|\.\./)", paper):
        raise ValueError("unexpected out-of-tree manuscript input")

    # Comments after the real document are fine, but non-comment LaTeX
    # after or multiple document endings indicate a corrupted source edit.
    if (paper.count(r"\end{document}") != 1
            or not paper.strip().endswith(r"\end{document}")):
        raise ValueError("manuscript has duplicate/premature end-of-document or trailing content")

    abstract = _ABSTRACT.search(main_text)
    if not abstract:
        raise ValueError("no parseable prospectively marked abstract")
    abstract_plain = re.sub(r"\\[A-Za-z]+\b(?:\s*\{)?", " ", abstract.group(1))
    words = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", abstract_plain)
    if not 150 <= len(words) <= 250:
        raise ValueError("abstract must contain 150-250 words for target journal")
    keywords = _KEYWORDS.search(paper)
    if not keywords or not 4 <= len(
            [x for x in keywords.group(1).split(",") if x.strip()]) <= 6:
        raise ValueError("target Springer keywords must number 4 to 6")

    cited = [token.strip() for match in _CITES.finditer(paper)
             for token in match.group(1).split(",")]
    bibkeys = _BIBKEY.findall(bib_text)
    if not cited:
        raise ValueError("paper needs citations")
    counts = Counter(bibkeys)
    if any(n != 1 for n in counts.values()):
        raise ValueError("duplicate BibTeX keys")
    missing = sorted(set(cited)-set(bibkeys))
    if missing:
        raise ValueError("missing citations: " + ",".join(missing))
    labels = _LABEL.findall(paper)
    nlabels = Counter(labels)
    if any(n != 1 for n in nlabels.values()):
        raise ValueError("duplicate LaTeX labels")
    refs = [token.strip() for match in _REFS.finditer(paper)
            for token in match.group(1).split(",")]
    unresolved = sorted(set(refs)-set(labels))
    if unresolved:
        raise ValueError("undefined LaTeX reference labels: " + ",".join(unresolved))

    env_stack: list[str] = []
    for kind, env in _BEGIN_END.findall(paper):
        if kind == "begin":
            env_stack.append(env)
        elif not env_stack or env_stack.pop() != env:
            raise ValueError("mismatched LaTeX environments")
    if env_stack:
        raise ValueError("unclosed LaTeX environments")
    if paper.count("\\section{Results}") != 1:
        raise ValueError("exactly one explicitly marked Results section required")
    comparison = audit_comparison_table(paper)
    if ("NO EMPIRICAL RQ RESULTS EXIST" not in main_text
            or "neither improved" not in paper.lower()
            or "independently" not in paper.lower()):
        raise ValueError("prospective result boundary or integrity status was removed")
    if "\\paragraph{Mixed evidence-versus-generation one-step decision.}" not in paper:
        raise ValueError("missing documented evidence/generation method boundary")
    if "sensitivity" not in paper or "finite-scenario" not in paper:
        raise ValueError("scenario diagnostic limitations no longer disclosed")

    return {
        "status": "SOURCE_INTEGRITY_AUDITED_NOT_LATEX_COMPILED",
        "springer_class_declared": "sn-jnl",
        "abstract_words_approximate": len(words),
        "keyword_count": len([x for x in keywords.group(1).split(",") if x.strip()]),
        "citations_used": len(set(cited)),
        "bibliography_entries": len(bibkeys),
        "undefined_citations": [],
        "undefined_crossreferences": [],
        "environment_delimiters_balanced": True,
        "real_rq_results_verified": False,
        "live_overleaf_modified": False,
        "novelty_comparison": comparison,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--main", type=Path, default=MAIN)
    p.add_argument("--bib", type=Path, default=BIB)
    args = p.parse_args(argv)
    print(json.dumps(audit_manuscript(
        args.main.read_text("utf-8"), args.bib.read_text("utf-8")),
        indent=2, sort_keys=True))
    print("SOURCE LINT ONLY; COMPILE IN AN OFFICIAL SPRINGER sn-jnl PROJECT.")


if __name__ == "__main__":
    main()
