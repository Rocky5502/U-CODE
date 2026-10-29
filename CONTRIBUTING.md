# Contributing to U-CODE

We welcome improvements to research methodology, reproducibility, source-only
validation, documentation and *safe* code. This is a prospective academic
project, not a working autonomous repair service.

## Development

```bash
python -m venv .venv
# Activate the environment for your OS.
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -m scripts.audit_overleaf_sources
python -m scripts.check_local_readiness
```

Open a feature branch and pull request. Include a short scientific purpose,
affected source/data assumptions, executed offline tests, and any limitations.
Never commit secrets, model weights, third-party source copies, evaluator-only
gold tests, or experimental claims not backed by independent receipts.
Source labels, evaluator authorization and task admission cannot be granted
by a pull request with a forged reviewer name.

- **Code style:** Python 3.10+ syntax, type hints and explicit error
  handling; deterministic stdlib tests with no live network calls.
- **Data:** preserve original GitHub identifiers and provenance; use a new
  versioned manifest rather than rewriting a frozen cohort or license.
- **Manuscript:** use verified primary references; declare prospective
  results as `N/A`; do not conflate a unit test with real task success.
- **Security:** maintain evaluator/policy separation, path allowlists,
  hard resource caps and a deny-by-default execution design.
- **Reviews:** the R0–R16 analytical personas are internal planning
  perspectives, **not independent human approvals**.

Original U-CODE work is [MIT-licensed](LICENSE), but linked external
models/datasets/repos may be subject to unrelated license terms and
provenance requirements. Human contributors are responsible for ensuring
they have the right to submit their changes.
