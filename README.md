# Administrative Discretion in Algorithmic Risk Assessment: Evidence from Spain’s VioGén System

This repository investigates how algorithmic risk assessment structures administrative discretion in Spain’s VioGén system. It combines longitudinal analysis of published risk classifications, a reconstruction of the historical VPR4.0 scoring instrument, and documentary analysis of the protocols governing police assessment and protection.

The central argument is that discretion is distributed across the production of assessment inputs, model specification and the procedural translation of classifications into police obligations. Officers’ formal authority to raise an automatic classification constitutes one decision point within this broader institutional arrangement.

The statistical analysis identifies a substantial reorganisation of the lowest published risk categories following the 2025 reform, alongside a comparatively small change in the national medium-or-above share: from 14.6% in June to 14.8% in July. The protocol analysis examines how judicial measures, reassessment requirements and inactivation conditions differentiate the consequences attached to those classifications.

## Data Sources

| Component | Sources | Coverage |
|---|---|---|
| Administrative statistics | Official monthly VioGén bulletins | National, regional, provincial and police-institution series, 2018–2026 |
| Historical scoring instrument | López Ossorio’s doctoral thesis and published VPR4.0 annexes | Indicator weights, thresholds, conditional relationships and completion instructions |
| Institutional framework | Instrucciones 4/2019, 5/2021 and 1/2025, supplemented by evidence on intervening instructions | Assessment authority, protection obligations, reassessment, inactivation and recording requirements |

The statistical dataset includes 96 nationally reconciled monthly observations and 93 months of regional and provincial coverage. The police-institution panel covers 71 months. Of these, 70 were extracted directly from the bulletins. The June 2025 observation comes from an earlier portal transcription that reconciles to the national bulletin total. Coverage gaps and verification status are recorded for each series.

## Analytical Approach

1. **Longitudinal and institutional comparison.** Examines changes in risk composition around protocol revisions, the November 2024 statistical discontinuity, and divergence between police institutions operating under a common assessment framework.
2. **Historical instrument reconstruction.** Implements the published VPR4.0 scoring rules and uses fictitious scenarios to examine the consequences of indicator coding, conditional dependencies and threshold placement.
3. **Comparative protocol analysis.** Codes decision authority, procedural conditions and protection requirements across the 2019 and 2025 protocols. Intervening changes are distinguished from provisions first documented in 2025, with claims graded by source quality.

## Repository Structure

| Directory | Contents |
|---|---|
| [data/](data/) | Statistical panels, scoring catalogues, scenarios and coded documentary records |
| [scripts/](scripts/) | Extraction, reconstruction and analysis code, notebooks, interactive interface and tests |
| [figures/](figures/) | Statistical charts and institutional diagrams |
| [sources/](sources/) | Primary documents, source-page excerpts and extraction evidence |
| [docs/](docs/) | Methods, verification records, detailed findings and limitations |

Matching subdirectories distinguish the statistical analysis, historical scoring reconstruction and institutional investigation.

## Replication

Run the following commands from the repository root with Python 3.11 or later.

```bash
python -m pip install -r requirements.txt
python -m pytest scripts/02_historical_scoring/tests scripts/03_institutional_rules/tests -q
```

| Component | Executed notebook | Documentation |
|---|---|---|
| Administrative statistics | [Monthly classifications](scripts/01_statistics/VioGen_2_Module1_Completed.ipynb) | [Data coverage and replication](docs/01_statistics/README.md) |
| Historical VPR4.0 | [Historical instrument reconstruction](scripts/02_historical_scoring/VioGen_Module2_Historical_Research_Lab.ipynb) | [Sources and verification](docs/02_historical_scoring/README.md) |
| Institutional rules | [Comparative protocol analysis](scripts/03_institutional_rules/VioGen_Module3_Research.ipynb) | [Documentary findings](docs/03_institutional_rules/FINDINGS_MEMO.md) |

## Scope and Interpretation

The historical reconstruction concerns VPR4.0. The weights and thresholds of VioGén 2 remain unpublished. Monthly statistics describe aggregate case stocks and cannot identify individual reclassification trajectories or causal reform effects. The documentary analysis establishes formal decision rules. Their implementation and the exercise of discretion in practice require additional evidence.
