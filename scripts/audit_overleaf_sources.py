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
