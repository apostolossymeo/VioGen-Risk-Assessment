# VioGén Module 3: who decides what, under the 2019 and 2025 police protocols

**Version 2. Verified and rebuilt.**

This is an institutional investigation of how the Spanish police protocols divide decisions between:
- officers;
- the system and its designers;
- courts and prosecutors;
- police management.

It compares Instrucción 4/2019 with Instrucción 1/2025, which introduced VioGén-2, and places both against the intervening instructions of 2021–2024.

It is **not** an algorithmic audit. It reconstructs no scoring, uses no real cases, and makes no claim about practice.

## Read in this order

1. [`FINDINGS_MEMO.md`](../../docs/03_institutional_rules/FINDINGS_MEMO.md): five findings, each split into documented / inference / unknown, with section and page references.
2. [`INTERVENING_INSTRUCTIONS_CHRONOLOGY.md`](../../docs/03_institutional_rules/INTERVENING_INSTRUCTIONS_CHRONOLOGY.md): which changes came in 2021–2024 rather than 2025, with evidence grades.
3. [`VALIDATION_REPORT.md`](../../docs/03_institutional_rules/VALIDATION_REPORT.md): what was verified and how, what was corrected from v1, and what could not be established.
4. [`SOURCE_VERIFICATION_MATRIX.csv`](../../data/03_institutional_rules/SOURCE_VERIFICATION_MATRIX.csv): 129 rows, one per claim (all v1 claims, new records, attributions).
5. [`VioGen_Module3_Research.ipynb`](../../scripts/03_institutional_rules/VioGen_Module3_Research.ipynb): the executed notebook walking through the evidence.
6. [`INTERVIEW_PROMPTS.md`](../../docs/03_institutional_rules/INTERVIEW_PROMPTS.md): questions for practitioners that the texts cannot answer.
7. [`CHANGELOG.md`](../../docs/03_institutional_rules/CHANGELOG.md): v1 → v2 file by file. The v1 datasets are kept in [`version1_data/`](../../data/03_institutional_rules/version1_data/), because the verification matrix audits them claim by claim.
8. [`PROTOTYPE_SPECIFICATION.md`](../../docs/03_institutional_rules/PROTOTYPE_SPECIFICATION.md): spec for the later live tool. **Not built.**

## Contents

| Path | What it holds |
|---|---|
| [`primary/`](../../sources/03_institutional_rules/primary/) | The three primary PDFs: 4/2019 (official), 1/2025 (signed CSV copy, mirror), 5/2021 (official) |
| [`text/`](../../sources/03_institutional_rules/text/) | The text used for matching: 2025 text layer, 2019 OCR, 5/2021 text layer |
| [`protocol_clauses.csv`](../../data/03_institutional_rules/protocol_clauses.csv) | 128 clause excerpts, each re-found on its declared page |
| [`decision_authority_rules.csv`](../../data/03_institutional_rules/decision_authority_rules.csv) | 55 decision-rule records: owner, modality, clauses, attribution, accountability trail |
| [`protocol_comparison.csv`](../../data/03_institutional_rules/protocol_comparison.csv) | 34 topics compared 2019 vs 2025, each with attribution and evidence grade |
| [`protection_measures_annex.csv`](../../data/03_institutional_rules/protection_measures_annex.csv) | Both annexes transcribed in full: 26 + 41 items |
| [`protection_measure_changes.csv`](../../data/03_institutional_rules/protection_measure_changes.csv) | 16 changes between the annexes |
| [`intervening_instructions.csv`](../../data/03_institutional_rules/intervening_instructions.csv) | 10 instruments, 2016–2025 |
| [`uncertainty_register.csv`](../../data/03_institutional_rules/uncertainty_register.csv) | 14 open questions |
| [`enumerated_abstract_pathways.csv`](../../data/03_institutional_rules/enumerated_abstract_pathways.csv) | 50 rule combinations; abstract, not cases |
| [`pathway_audit_v1_vs_v2.csv`](../../data/03_institutional_rules/pathway_audit_v1_vs_v2.csv) | v1 engine against v2 engine |
| [`research_export.json`](../../data/03_institutional_rules/research_export.json) | Everything above in one JSON for the later tool |
| [`source_ledger.csv`](../../data/03_institutional_rules/source_ledger.csv) | 11 sources, with hashes, hosts and access notes |
| [`src/`](../../scripts/03_institutional_rules/src/) | Sources and clauses, records, annex items, quote checker, decision-rule engine |
| [`03_institutional_rules/`](../../figures/03_institutional_rules/) | 01 change chronology · 02 decision-authority map 2025 · 03 low-risk restructuring · 04 annex modalities |
| [`tests/`](../../scripts/03_institutional_rules/tests/) | 52 test functions, 275 cases |

## Reproduce

Run these commands from the repository root.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python3 scripts/03_institutional_rules/build_module3.py      # rebuilds data/ and the matrix (deterministic)
python3 scripts/03_institutional_rules/make_figures.py       # rebuilds figures/
python3 scripts/03_institutional_rules/make_notebook.py      # rebuilds the notebook from src/
jupyter nbconvert --to notebook --execute --inplace scripts/03_institutional_rules/VioGen_Module3_Research.ipynb
python3 -m pytest scripts/03_institutional_rules/tests -q    # 275 passed
```

## Ground rules kept throughout

- **"Verified"** means found on the declared page of a primary text.
- **Evidence grades:**
  - A: primary text;
  - B: official summary;
  - C: secondary source;
  - D: no evidence.
- No deadline is inferred when its prerequisites are absent. Unknown facts stay unknown.
- A change first *documented* in 2025 is not called *introduced* in 2025 unless the evidence allows it.
- Module 2's VPR4.0 (2016) is not VioGén-2.

## Copyright

Spanish official instructions are excluded from copyright protection (art. 13 TRLPI). Press and academy texts are cited by URL and not redistributed.
