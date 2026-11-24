"""Fictitious worked examples for the historical VPR4.0 laboratory. No real person or case.

Every example is a fully specified hypothetical form: listed rows are Sí, rows listed as unknown are "No se sabe",
every other row is No. Parent questions of selected sub-items are set to Sí (the form asks sub-items
"en caso afirmativo"). Scores are historical additive units, not probabilities or measures of danger.
Run: python demo_scenarios.py  (writes hypothetical_scenarios.csv / .json)
"""
import csv
import json
from pathlib import Path

from vpr4_historical import evaluate, exact_cutoff_examples, indicator_count_example, make_case, max_indicators_example

DATA = Path(__file__).resolve().parents[2] / 'data' / '02_historical_scoring'

SCENARIOS = [
    # name, Sí rows, unknown rows, what the example is for
    ('all_rows_no', [], [], 'Baseline: every row answered No.'),
    ('firearm_used', ['I5_firearm_use'], [], 'F02 (1.533) + firearm sub-item (0.000). Not a statement about the danger of firearms.'),
    ('knife_used', ['I5_knife'], [], 'F02 (1.533) + knife sub-item (4.000, critical indicator no. 3, p. 193).'),
    ('firearm_and_knife_used', ['I5_firearm_use', 'I5_knife'], [], 'Sub-items are checkboxes ("se pueden marcar varias opciones", p. 294): both can be ticked.'),
    ('firearm_access_without_use', ['I6_firearm_access'], [], 'I6 is assessed independently of F02 (p. 295) and weighs 0.'),
    ('death_threat_escalation', ['I7_death_threat', 'I8_escalation'], [], 'F03 (0) + death threat (2.800) + escalation (2.800).'),
    ('stalking_separation', ['I11_stalking', 'I36_recent_separation'], [], 'Two critical indicators, still below the first cut-off.'),
    ('stalking_separation_fear', ['I11_stalking', 'I36_recent_separation', 'I39_victim_fear_lethal'], [],
     "Adding the victim's own perception (I39) crosses 9.535."),
    ('coding_choice_without_insults', ['I11_stalking', 'I36_recent_separation'], [],
     'Input discretion, version A: the officer does not record the insults as psychological violence.'),
    ('coding_choice_with_insults', ['I11_stalking', 'I36_recent_separation', 'I1_psychological'], [],
     'Input discretion, version B: the same account, with the insults recorded as I1 (1.428). The level changes.'),
    ('severity_choice_leve', ['I11_stalking', 'I36_recent_separation', 'I2_physical'], [],
     'Physical violence recorded as "leve" (no severity points).'),
    ('severity_choice_grave', ['I11_stalking', 'I36_recent_separation', 'I2_physical_severe'], [],
     'Same episode recorded as "grave". Annex 5 tells officers to choose the more severe level when in doubt (pp. 292-294).'),
    ('record_prior_aggression', ['I18_prior_aggression'], [],
     'I18 is asked only if F08 (criminal/police record) is Sí (p. 301): 2.142 + 1.870. Version 1 scored 1.870.'),
    ('unknowns_leave_level_open', ['I11_stalking', 'I36_recent_separation'], ['I39_victim_fear_lethal', 'I9_jealousy'],
     'Two answers "No se sabe": the score lies between 8.226 and 14.596, spanning two levels.'),
]


def run():
    out = []
    for name, yes, unknown, purpose in SCENARIOS:
        e = evaluate(make_case(*yes, unknown=unknown))
        out.append(dict(name=name, selected_rows=yes, unknown_rows=unknown, score_min=e['score_min'],
                        score_max=e['score_max'], category=e['category'] or 'undetermined (unknown answers)',
                        category_at_min=e['category_at_min'], category_at_max=e['category_at_max'],
                        indicators_present=len(e['indicators_present']), purpose=purpose))
    m = max_indicators_example()
    e = m['evaluation']
    out.append(dict(name='most_indicators_still_no_appreciable', selected_rows=m['codes'], unknown_rows=[],
                    score_min=e['score_min'], score_max=e['score_max'], category=e['category'],
                    category_at_min=e['category_at_min'], category_at_max=e['category_at_max'],
                    indicators_present=len(e['indicators_present']),
                    purpose=f"Exact maximum: {m['indicators']} of the 39 indicators can be Sí while the score stays in "
                            "No apreciado. Logical possibility under the form structure, not an observed case."))
    m = indicator_count_example('Extreme', most=False)
    e = m['evaluation']
    out.append(dict(name='fewest_indicators_extreme', selected_rows=m['codes'], unknown_rows=[],
                    score_min=e['score_min'], score_max=e['score_max'], category=e['category'],
                    category_at_min=e['category_at_min'], category_at_max=e['category_at_max'],
                    indicators_present=len(e['indicators_present']),
                    purpose=f"Exact minimum: {m['indicators']} indicators ({m['facts']} facts counting the weighted "
                            "factor questions F02/F03/F08) are enough for Extremo. The other route to a level (p. 192)."))
    for ex in exact_cutoff_examples()[:1]:
        e = evaluate(make_case(*ex['codes']))
        out.append(dict(name='exactly_at_first_cutoff', selected_rows=ex['codes'], unknown_rows=[], score_min=e['score_min'],
                        score_max=e['score_max'], category=e['category'], category_at_min=e['category_at_min'],
                        category_at_max=e['category_at_max'], indicators_present=len(e['indicators_present']),
                        purpose=f"Scores exactly {ex['cutoff']}: {ex['inclusive_reading']} if 'hasta' is inclusive, "
                                f"{ex['exclusive_reading']} otherwise."))
    return out


if __name__ == '__main__':
    rows = run()
    (DATA / 'hypothetical_scenarios.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf-8')
    with (DATA / 'hypothetical_scenarios.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows({**r, 'selected_rows': '; '.join(r['selected_rows']), 'unknown_rows': '; '.join(r['unknown_rows'])}
                    for r in rows)
    for r in rows:
        print(f"{r['name']:40s} {r['score_min']:7.3f}-{r['score_max']:7.3f}  {r['category']}")
