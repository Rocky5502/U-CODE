"""Generate 1,000 research-review *perspectives*, not 1,000 people.

Twenty domain chairs x ten concrete focal risks x five distinct expert audit
roles = 1,000 clearly PENDING questions. This is a scoping register; it does
NOT certify review, correctness, novelty, human independence or any experiment.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

AREAS = [
  [
    "SBSE_FORMALIZATION",
    [
      "decision state sufficiency",
      "action set and stop action",
      "Pareto versus scalar objective",
      "cost scalarization",
      "constraint feasibility",
      "planning horizon",
      "candidate archive capacity",
      "dominance and pruning",
      "termination semantics",
      "optimality scope"
    ]
  ],
  [
    "BAYES_AND_CALIBRATION",
    [
      "prior calibration",
      "class conditional likelihoods",
      "posterior predictive mass",
      "zero likelihood evidence",
      "Bayes martingale",
      "conditional ECE validity",
      "base rate shift",
      "nested data fitting",
      "label leakage",
      "uncertainty uncertainty"
    ]
  ],
  [
    "CORRELATED_EVIDENCE",
    [
      "shared test errors",
      "reused oracle symptoms",
      "redundant diagnostics",
      "history-conditioned likelihood",
      "branch normalization",
      "unobserved history",
      "cross candidate dependence",
      "joint truth atoms",
      "producer-conditioned priors",
      "off-support evidence"
    ]
  ],
  [
    "SEARCH_ALGORITHMS",
    [
      "finite tree recurrence",
      "generation transitions",
      "repair parent conditioning",
      "search tie breaking",
      "state memoization",
      "terminal threshold",
      "cost double charging",
      "candidate diversity",
      "action re-use",
      "asymptotic complexity"
    ]
  ],
  [
    "CODE_AGENT_INTEGRATION",
    [
      "public observation interface",
      "frozen action catalog",
      "candidate patch provenance",
      "context retrieval influence",
      "generation failure semantics",
      "LLM tool output trust",
      "agent loop stopping",
      "patch SHA identity",
      "sandbox feedback routing",
      "rollbacks and retries"
    ]
  ],
  [
    "DATA_PROVENANCE",
    [
      "PR discovery unit",
      "agent authorship",
      "commit SHA pinning",
      "fork lineage",
      "source-era issue text",
      "patch attribution",
      "search-language mismatch",
      "mixed-license files",
      "archive selection",
      "deduplication"
    ]
  ],
  [
    "DATA_QUALITY",
    [
      "metadata completeness",
      "primary key uniqueness",
      "schema drift",
      "language strata",
      "missingness",
      "source URL validity",
      "temporal snapshot",
      "outlier triage",
      "join invariants",
      "dataset release hashes"
    ]
  ],
  [
    "TASK_ADMISSION",
    [
      "task-era specification",
      "rights clearance",
      "functionality oracle",
      "oracle separation",
      "source reuse",
      "reproducible toolchain",
      "rootless containment",
      "resource caps",
      "external adjudication",
      "reconstructed task labeling"
    ]
  ],
  [
    "SOFTWARE_ORACLES",
    [
      "independent expected behavior",
      "regression fixture independence",
      "hidden test correctness",
      "false pass risk",
      "false fail risk",
      "environment ambiguity",
      "flaky tests",
      "nondeterministic outputs",
      "cross-platform behavior",
      "oracle coverage"
    ]
  ],
  [
    "MODEL_SELECTION",
    [
      "six-ID identity",
      "weights commit freeze",
      "tokenizer freeze",
      "terms acceptance",
      "quantization fidelity",
      "engine version",
      "memory feasibility",
      "prompt hashing",
      "sampling seed",
      "model family overlap"
    ]
  ],
  [
    "GPU_EXECUTION",
    [
      "VRAM measurement",
      "GPU occupancy",
      "CUDA runtime",
      "throughput",
      "time-to-first-token",
      "OOM failures",
      "backend fallback",
      "driver pinning",
      "thermal variability",
      "batch and context limits"
    ]
  ],
  [
    "SYSTEM_SECURITY",
    [
      "no network in sandbox",
      "rootless execution",
      "read-only source",
      "filesystem escape",
      "process isolation",
      "secret leakage",
      "model remote code",
      "supply chain review",
      "artifact quarantine",
      "execution log integrity"
    ]
  ],
  [
    "RESOURCE_ACCOUNTING",
    [
      "token usage",
      "test call counts",
      "GPU wall seconds",
      "CPU time",
      "elapsed time",
      "controller overhead",
      "per-action receipts",
      "cgroup limits",
      "cost parity",
      "timeout semantics"
    ]
  ],
  [
    "EXPERIMENTAL_DESIGN",
    [
      "primary estimand",
      "randomization unit",
      "task-model pairing",
      "seed pairing",
      "precommitment",
      "policy fidelity",
      "baseline strength",
      "negative controls",
      "ablation isolation",
      "stopping rules"
    ]
  ],
  [
    "METRICS_AND_STATS",
    [
      "ITT denominator",
      "release coverage",
      "wrong-release risk",
      "conditional denominator",
      "missingness bounds",
      "cluster bootstrap",
      "multiple testing",
      "calibration drift",
      "effect size units",
      "uncertainty intervals"
    ]
  ],
  [
    "BASELINES",
    [
      "MCTS fidelity",
      "replay search fidelity",
      "fixed test comparison",
      "uncertainty-only control",
      "strong no-uncertainty search",
      "adaptive verification",
      "equal tool access",
      "matched seed budget",
      "oracle blindness",
      "implementation audit"
    ]
  ],
  [
    "MULTILINGUAL_SE",
    [
      "Python tasks",
      "JavaScript tasks",
      "TypeScript tasks",
      "Java tasks",
      "Go tasks",
      "Rust tasks",
      "C and C++ tasks",
      "C# tasks",
      "Kotlin tasks",
      "PHP and Ruby tasks"
    ]
  ],
  [
    "REPRODUCIBILITY",
    [
      "clean install",
      "Python 3.10",
      "Python 3.12",
      "dependency pin",
      "deterministic tests",
      "source hashes",
      "artifact version",
      "OS portability",
      "CI permissions",
      "independent replication"
    ]
  ],
  [
    "LITERATURE_NOVELTY",
    [
      "SWE-Search overlap",
      "ICML guided search overlap",
      "selective verification prior art",
      "PATSSEL comparison",
      "SWE-Replay comparison",
      "RETRACE comparison",
      "Dockerless comparison",
      "method naming precision",
      "negative-results framing",
      "OpenCoderX CALM-SE overlap"
    ]
  ],
  [
    "SPRINGER_PUBLICATION",
    [
      "statement scope",
      "abstract evidence",
      "equation labels",
      "algorithm pseudocode",
      "primary-source citations",
      "table meaning",
      "figure provenance",
      "funding and authorship",
      "artifact availability",
      "final scientific claims"
    ]
  ]
]
PERSPECTIVES = [
  [
    "THEORIST",
    "State explicit assumptions, the mathematical claim and a precise falsifier"
  ],
  [
    "IMPLEMENTATION_AUDITOR",
    "Identify code paths, invariant boundaries and an implementation failure mode"
  ],
  [
    "ADVERSARIAL_TESTER",
    "Design one small reproducible counterexample or invariant test"
  ],
  [
    "EMPIRICAL_REVIEWER",
    "Check sampling, correctness oracle, controls and inference threats"
  ],
  [
    "REPRODUCIBILITY_EDITOR",
    "Specify minimal frozen inputs, executable check and evidence receipt"
  ]
]

def build_registry() -> dict:
    if len(AREAS) != 20 or len(PERSPECTIVES) != 5:
        raise AssertionError("twenty research domains and five audit roles required")
    if len({name for name, _ in AREAS}) != 20:
        raise AssertionError("research domain names must be unique")
    if len({name for name, _ in PERSPECTIVES}) != 5:
        raise AssertionError("reviewer-role lens names must be unique")
    rows = []
    for domain, topics in AREAS:
        if len(topics) != 10 or len(set(topics)) != 10:
            raise AssertionError("ten specific non-duplicated topics per domain")
        for topic_index, topic in enumerate(topics, 1):
            for role, instruction in PERSPECTIVES:
                rows.append({
                    "lens_id": f"{domain}.{topic_index:02d}.{role}",
                    "domain": domain,
                    "research_risk": topic,
                    "perspective": role,
                    "review_question": instruction + " for: " + topic,
                    "review_status": "PENDING_NOT_EXECUTED",
                    "evidence_artifacts": [],
                    "human_reviewer_attestation": False,
                    "experiment_evidence": False,
                })
    ids = {r["lens_id"] for r in rows}
    if len(rows) != 1000 or len(ids) != 1000:
        raise AssertionError("exactly 1000 distinct pending audit lenses")
    return {
        "schema_version": "1.0",
        "purpose": "RESEARCH_SCOPING_ONLY",
        "roles_mean_simulated_review_perspectives_not_people": True,
        "domain_chairs": 20,
        "risk_topics_per_domain": 10,
        "perspective_roles_per_risk": 5,
        "lens_count": len(rows),
        "completed_real_reviews": 0,
        "external_expert_signoffs": 0,
        "research_evidence_claimed": False,
        "lenses": rows,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("dist/ucode-review-1000-lenses.json"))
    args = parser.parse_args()
    result = build_registry()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k != "lenses"},
                     sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
