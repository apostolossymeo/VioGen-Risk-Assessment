"""Rebuild every Module 3 dataset, the verification matrix and the research export from the records in src/.

    python build_module3.py          (then: python make_figures.py; python make_notebook.py)

Deterministic: running it twice produces byte-identical files.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))

from annex_measures import MEASURE_CHANGES, MEASURES  # noqa: E402
from decision_rules import LEVELS, enumerate_abstract_pathways  # noqa: E402
from module3_records import CHRONOLOGY, COMPARISON, RULES, UNCERTAINTY  # noqa: E402
from module3_sources import CLAUSES, SOURCES, clause  # noqa: E402
from quote_check import locate  # noqa: E402

DATA = ROOT.parents[1] / 'data' / '03_institutional_rules'
DATA.mkdir(exist_ok=True)
ARCH = DATA / 'version1_data'


def write(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    fields = fields or list(rows[0].keys())
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: ('' if r.get(k) is None else r.get(k)) for k in fields})


def clause_pages(ids: str) -> str:
    out = []
    for cid in [x.strip() for x in ids.split(';') if x.strip()]:
        c = clause(cid)
        out.append(f"{c['source_id']} {c['section']} p.{c['pdf_pages']}")
    return ' | '.join(out)


def clause_quotes(ids: str, limit: int = 2) -> str:
    qs = []
    for cid in [x.strip() for x in ids.split(';') if x.strip()][:limit]:
        q = clause(cid)['quote_es']
        qs.append(f'[{cid}] "{q[:260]}{"…" if len(q) > 260 else ""}"')
    return ' '.join(qs)


def main() -> None:
    # ---------------------------------------------------------------- sources and clauses
    write(DATA / 'source_ledger.csv', SOURCES)
    crow = []
    for c in CLAUSES:
        r = locate(c['source_id'], c['quote_es'], c['pdf_pages'])
        crow.append(dict(c, quote_found_on_declared_page=r['found'], match_method=r['method'], match_score=r['score']))
    write(DATA / 'protocol_clauses.csv', crow)

    # ---------------------------------------------------------------- rules
    rrows = []
    for r in RULES:
        rrows.append(dict(r, source_id='SES-4-2019' if r['protocol'] == 2019 else 'SES-1-2025',
                          source_locations=clause_pages(r['clause_ids'])))
    write(DATA / 'decision_authority_rules.csv', rrows,
          ['rule_id', 'protocol', 'stage', 'decision_point', 'decision_owner', 'other_actors', 'modality', 'rule_summary_en',
           'clause_ids', 'source_locations', 'source_id', 'v1_status', 'correction_note', 'attribution', 'accountability_trail', 'interpretive_note'])

    # ---------------------------------------------------------------- comparison, chronology, uncertainty
    write(DATA / 'protocol_comparison.csv', COMPARISON)
    write(DATA / 'intervening_instructions.csv', CHRONOLOGY)
    write(DATA / 'uncertainty_register.csv',
          [dict(zip(['item_id', 'type', 'question', 'current_evidence', 'confidence', 'how_to_resolve'], u)) for u in UNCERTAINTY])

    # ---------------------------------------------------------------- measures (complete annexes) and their changes
    mrows = []
    for m in MEASURES:
        r = locate(m['source_id'], m['text_es'], m['pdf_page'])
        mrows.append(dict(m, text_found_on_declared_page=r['found']))
    write(DATA / 'protection_measures_annex.csv', mrows)
    write(DATA / 'protection_measure_changes.csv',
          [dict(zip(['topic', 'measure_2019', 'measure_2025', 'change_type', 'note'], c)) for c in MEASURE_CHANGES])

    # ---------------------------------------------------------------- audited v1 selected measures
    v1m = list(csv.DictReader(open(ARCH / 'selected_protective_measures.csv', encoding='utf-8')))
    audit = [('A2-2025-02', 'qualified', 'In the all-levels row of Annex II (and its header), not specific to Bajo.'),
             ('A2-2025-04; A2-2025-05', 'verified', ''),
             ('A2-2025-07', 'verified', '"Información y, en su caso, derivación".'),
             ('A2-2025-09', 'qualified', 'Page 37 only; the phrase is "en función de los medios disponibles".'),
             ('A2-2025-19', 'verified', ''), ('A2-2025-21', 'verified', '"Vigilancia ocasional y aleatoria".'),
             ('A2-2025-22', 'verified', ''), ('A2-2025-27', 'verified', ''), ('A2-2025-30', 'verified', ''),
             ('A2-2025-32', 'verified', 'Adds "de manera presencial por parte del Cuerpo Policial respectivo".'),
             ('A2-2025-35', 'verified', ''), ('A1-2019-02; A1-2019-03', 'verified', ''),
             ('A1-2019-07', 'qualified', '2019 modality is agreed with the victim (uniform, vehicles), not resource-contingent.')]
    out = []
    for r, (mid, st, note) in zip(v1m, audit):
        out.append(dict(r, measure_ids_v2=mid, audit_status=st, audit_note=note,
                        exhaustive='False (v1 selection); the complete annexes are in protection_measures_annex.csv'))
    write(DATA / 'selected_protective_measures.csv', out)

    # ---------------------------------------------------------------- pathways and audit against v1
    paths = enumerate_abstract_pathways()
    write(DATA / 'enumerated_abstract_pathways.csv', paths)
    v1p = list(csv.DictReader(open(ARCH / 'enumerated_abstract_pathways.csv', encoding='utf-8')))
    idx = {(int(p['year']), p['assigned_category'], p['officer_category'], p['judicial_measures'] == 'True'): p for p in v1p}
    arows = []
    for p in paths:
        o = idx[(p['year'], p['assigned_category'], p['officer_category'], p['judicial_measures'])]
        diffs = []
        f1 = o['first_vper_max_days'] or None
        f2 = None if p['first_vper_max_days'] is None else str(p['first_vper_max_days'])
        if f1 != f2:
            diffs.append(f'first_vper_max_days {f1} -> {f2}')
        l1 = o['later_vper_before_days']
        l2 = f"{p['later_vper_value']} {p['later_vper_unit']}"
        if not (l1 == str(p['later_vper_value']) or (l1 == '3' and l2 == '72 hours')):
            diffs.append(f'later_vper {l1} -> {l2}')
        elif l1 == '3':
            diffs.append('later_vper 3 (days) -> 72 hours (unit made explicit)')
        semantic = []
        label_map = {('not_eligible_under_ordinary_rule', 'not_eligible'): 'label',
                     ('unknown_conditions', 'cannot_determine'): 'label',
                     ('possible_subject_to_professional_review', 'cannot_determine'): 'v1 assumed the evaluator-judgement premise (2.6.ii) was met',
                     ('insufficient_conditions', 'cannot_determine'): 'v1 treated unknown premises (None) as unmet'}
        key = (o['ordinary_inactivation_review'], p['ordinary_inactivation'])
        if key[0] != key[1]:
            kind = label_map.get(key, 'unexplained')
            (diffs if kind == 'label' else semantic).append(f'inactivation {key[0]} -> {key[1]}' + ('' if kind == 'label' else f' ({kind})'))
        arows.append(dict(pathway_id=p['pathway_id'], year=p['year'], assigned=p['assigned_category'], officer=p['officer_category'],
                          judicial_measures=p['judicial_measures'],
                          deadlines_consistent_with_text='yes' if not [d for d in diffs if d.startswith('first') or (d.startswith('later') and 'explicit' not in d)] else 'no',
                          inactivation_semantics='ok' if not semantic else 'v1 error',
                          differences='; '.join(diffs + semantic) or 'none'))
    write(DATA / 'pathway_audit_v1_vs_v2.csv', arows)

    # ---------------------------------------------------------------- verification matrix (claim by claim)
    write(DATA / 'SOURCE_VERIFICATION_MATRIX.csv', verification_matrix(),
          ['claim_id', 'origin', 'claim_as_in_v1', 'verified_statement_v2', 'source_id', 'source_url', 'location', 'evidence_excerpt_es',
           'status', 'change_made', 'confidence'])

    # ---------------------------------------------------------------- research export (for a later app; not an app)
    export = dict(
        schema='viogen-module3-research-export/2.0', generated_by='build_module3.py', status='research data, verified against the protocol texts; NOT application logic',
        disclaimer='Formal rules from two protocol texts. No risk scoring, no real cases, no statement about police practice.',
        levels={str(k): list(v) for k, v in LEVELS.items()},
        sources=SOURCES, clauses=CLAUSES, rules=RULES, comparison=COMPARISON, measures=MEASURES,
        measure_changes=[dict(zip(['topic', 'measure_2019', 'measure_2025', 'change_type', 'note'], c)) for c in MEASURE_CHANGES],
        chronology=CHRONOLOGY,
        uncertainty=[dict(zip(['item_id', 'type', 'question', 'current_evidence', 'confidence', 'how_to_resolve'], u)) for u in UNCERTAINTY],
        abstract_pathways=paths)
    (DATA / 'research_export.json').write_text(json.dumps(export, ensure_ascii=False, indent=1, sort_keys=False) + '\n', encoding='utf-8')
    print(f'sources {len(SOURCES)} | clauses {len(CLAUSES)} | rules {len(RULES)} | comparison {len(COMPARISON)} | '
          f'measures {len(MEASURES)} | pathways {len(paths)} | matrix rows {len(verification_matrix())}')


V1_COMPARISON_MAP = {
    'Risk levels': ('T01', 'verified', ''),
    'Upward-only police override': ('T03', 'qualified', 'Continuity confirmed and traced further back: Instrucción 7/2016 rule 1.5 and the 2019 preamble.'),
    'Data entry and source corroboration': ('T05', 'verified', 'Added: the 2019 "no direct questions" clause has no 2025 counterpart.'),
    'Trigger after new violent incident': ('T09', 'verified', 'Added the breach trigger and the Cometa route (2025 §8).'),
    'First routine VPER cap for medium+': ('T11', 'corrected', 'The 2019 7-day cap covers BAJO and above, not only medium+; 2025 Bajo without measures has no stated deadline.'),
    'Later VPER: extreme/high/medium': ('T13', 'verified', ''),
    'Later VPER: lowest classification': ('T14', 'verified', ''),
    'Routine VPER reporting to courts': ('T15', 'verified', ''),
    'Mandatory protection tiers': ('T16', 'qualified', 'The obligation structure is continuous, but the content of the floor changed (T29-T34).'),
    'Escalating capacity constraints': ('T17', 'verified', ''),
    'Ordinary inactivation': ('T18', 'qualified', '2019 premises completed; 2025 premise is a positive finding; attribution to 2/2024 (grade B) for the in-person contact.'),
    'Supervision state': ('T22', 'corrected', 'Created by Instrucción 2/2024 (not 2022). 2025 shortened several 2024 parameters (grade C).'),
    'Personalised safety plan': ('T27', 'verified', 'PSP dates from Instrucción 7/2016.'),
    'General case status with current court measures': ('T16', 'verified', 'See rules 2019-R14 / 2025-R14.'),
    'Evaluation without complaint': ('T06', 'corrected', 'The ex officio duty is in the 2019 text; Protocolo Cero (2021) added first-contact procedure only.'),
    'Consolidated VPR': ('T07', 'verified', 'Origin of the 72-hour limit unknown.'),
}

HYPOTHESES = [
    ('H1', 'Upward-only officer adjustment was already documented in 2019: not a 2025 innovation.', 'verified',
     'Verified; it also predates 2019 (7/2016 rule 1.5; 2019 preamble).', 'C19-1.6; C19-5.10; C19-PRE-OVR; C25-3.8; C25-6.2', 'high'),
    ('H2', 'Five risk categories in 2019 vs four in 2025, following removal of no apreciado.', 'verified', 'Verified.', 'C19-1.6; C25-3.8-LEV; C25-PREL-NA', 'high'),
    ('H3', 'New event: 2019 VPER-C vs 2025 new VPR.', 'verified', 'Verified for a new complaint or breach; 2025 also uses VPR after a verified Cometa breach and for requests linked to a possible reoffence.', 'C19-5.2-C; C25-4.2; C25-4.1; C25-8-COMETA', 'high'),
    ('H4', '2019 first VPER within 7 days; 2025 within 15 days for medium/high/extreme.', 'qualified',
     '2019: 7 days for bajo and above (and no apreciado with measures). 2025: 15 days for Medio+ and Bajo with measures; none stated for Bajo without measures. Special relevance: a 7-day MINIMUM in both.', 'C19-5.3; C19-5.4; C19-5.5; C25-4.3; C25-4.4; C25-4.5', 'high'),
    ('H5', '2025 later low-risk VPER 60 vs 90 days by judicial measures, under eligibility conditions.', 'verified',
     'Verified: after the first VPER, without known incidents, while active; "medidas o penas judiciales en vigor".', 'C25-6.1; C25-6.1-BAJO', 'high'),
    ('H6', 'Court-notification language in routine VPER differs; narrow procedure.', 'verified',
     'Verified: 2019 any variation (VPER-S); 2025 only upward. Other duties (incident files, inactivation oficios) remain.', 'C19-5.11; C19-5.12; C25-6.3', 'high'),
    ('H7', 'Supervision/inactivation rules differ; identify intervening origins and exceptions.', 'verified',
     'Supervised cases created by Instrucción 2/2024 (official summary, grade B); non-location 1 -> 6 (2024, grade C) -> 3 months; renunciation narrowed in 2024 and 2025.', 'C25-7.4.1-ER; C25-7.2.1-LOC; C25-7.2.2; C19-2.7; C19-2.8', 'medium'),
]


def verification_matrix() -> list[dict]:
    url = {s['source_id']: s['url'] for s in SOURCES}
    rows = []
    v1r = {r['rule_id']: r for r in csv.DictReader(open(ARCH / 'decision_authority_rules.csv', encoding='utf-8'))}
    for r in RULES:
        o = v1r.get(r['rule_id'])
        sid = 'SES-4-2019' if r['protocol'] == 2019 else 'SES-1-2025'
        rows.append(dict(claim_id=r['rule_id'], origin='v1_rule' if o else 'v2_new_rule',
                         claim_as_in_v1=(f"{o['documented_rule_summary']} [§{o['source_section']}, p.{o['printed_page']}]" if o else ''),
                         verified_statement_v2=r['rule_summary_en'], source_id=sid, source_url=url[sid],
                         location=clause_pages(r['clause_ids']), evidence_excerpt_es=clause_quotes(r['clause_ids']),
                         status=r['v1_status'] if o else 'new_verified', change_made=r['correction_note'], confidence='high'))
    assert len([r for r in rows if r['origin'] == 'v1_rule']) == 35
    for o in csv.DictReader(open(ARCH / 'protocol_comparison.csv', encoding='utf-8')):
        tid, st, note = V1_COMPARISON_MAP[o['topic']]
        t = next(x for x in COMPARISON if x['topic_id'] == tid)
        rows.append(dict(claim_id=f'v1-cmp:{o["topic"]}', origin='v1_comparison',
                         claim_as_in_v1=f"2019: {o['protocol_2019']} | 2025: {o['protocol_2025']} | {o['classification']}",
                         verified_statement_v2=f"{tid}: 2019: {t['protocol_2019']} | 2025: {t['protocol_2025']} | attribution: {t['attribution']} ({t['evidence_grade']})",
                         source_id='SES-4-2019; SES-1-2025', source_url=f"{url['SES-4-2019']} ; {url['SES-1-2025']}",
                         location=f"v1: {o['source_2019']} ; {o['source_2025']}", evidence_excerpt_es='', status=st, change_made=note,
                         confidence='high' if t['evidence_grade'] == 'A' else 'medium'))
    for m in csv.DictReader(open(DATA / 'selected_protective_measures.csv', encoding='utf-8')):
        ids = [x.strip() for x in m['measure_ids_v2'].split(';')]
        mm = [x for x in MEASURES if x['measure_id'] in ids]
        rows.append(dict(claim_id=f"v1-measure:{m['year']}:{m['level']}:{m['measure_summary'][:40]}", origin='v1_measure',
                         claim_as_in_v1=f"{m['measure_summary']} [{m['obligation_type']}; p.{m['printed_page']}]",
                         verified_statement_v2='; '.join(f"{x['measure_id']}: {x['summary_en']} ({x['modality']})" for x in mm),
                         source_id=mm[0]['source_id'], source_url=url[mm[0]['source_id']],
                         location='; '.join(f"{x['annex']} p.{x['pdf_page']}" for x in mm),
                         evidence_excerpt_es=' / '.join(x['text_es'][:200] for x in mm), status=m['audit_status'], change_made=m['audit_note'], confidence='high'))
    for hid, claim, st, verdict, cids, conf in HYPOTHESES:
        rows.append(dict(claim_id=hid, origin='initial_hypothesis', claim_as_in_v1=claim, verified_statement_v2=verdict,
                         source_id='SES-4-2019; SES-1-2025', source_url=f"{url['SES-4-2019']} ; {url['SES-1-2025']}",
                         location=clause_pages(cids), evidence_excerpt_es=clause_quotes(cids, 3), status=st, change_made='', confidence=conf))
    prov = [
        ('S1', 'Official 2019 instruction at the igualdad.gob.es URL.', 'verified', 'Downloaded; 23 pages, scanned (no text layer); printed page = PDF page; signed 6 March 2019, effective 13 March 2019.', 'SES-4-2019', 'C19-EFF', 'high'),
        ('S2', '2025 signed text via third-party mirror with CSV GEN-61b6-a6bd-ca9d-fb9e-612a-3074-2815-598b.', 'qualified',
         'Verified the CSV, signer and date on every page; two hosts byte-identical, a third text-identical. Official CSV validation not performed (captcha). No government host found.', 'SES-1-2025', 'C25-EFF', 'medium-high'),
        ('S3', 'v1: primary PDFs could not be downloaded or bundled; Annex II not visually checked.', 'superseded',
         'All three primary PDFs downloaded, hashed and bundled; Annex II pp. 37-40 checked against page images and fully transcribed.', 'SES-1-2025', 'C25-A2-CUM', 'high'),
        ('S4', 'v1: 2025 consolidates intervening 2021/2022/2024 instructions.', 'qualified',
         'The 2025 derogation list (p. 4) names 4/2019, 7/2019, 8/2021, 11/2022, 1/2023, 2/2024; Protocolo Cero 5/2021 stays in force.', 'SES-1-2025', 'C25-DEROG', 'high'),
    ]
    for pid, claim, st, verdict, sid, cid, conf in prov:
        rows.append(dict(claim_id=pid, origin='provenance', claim_as_in_v1=claim, verified_statement_v2=verdict, source_id=sid, source_url=url[sid],
                         location=clause_pages(cid), evidence_excerpt_es=clause_quotes(cid, 1), status=st, change_made='', confidence=conf))
    for t in COMPARISON:
        rows.append(dict(claim_id=f'attribution:{t["topic_id"]}', origin='v2_change_attribution', claim_as_in_v1='',
                         verified_statement_v2=f"{t['topic']}: {t['attribution']} — {t['attribution_evidence']}", source_id='see chronology',
                         source_url='', location=t['rule_ids'], evidence_excerpt_es='', status=f"grade {t['evidence_grade']}", change_made='',
                         confidence={'A': 'high', 'B': 'medium-high', 'C': 'medium', 'D': 'low'}[t['evidence_grade'][0]]))
    return rows


if __name__ == '__main__':
    main()
