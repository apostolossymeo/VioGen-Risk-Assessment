"""Write SOURCE_VERIFICATION_MATRIX.csv: one line per Annex 1 row, then one line per method/procedure claim.

Run from the package folder:
    python tools/build_verification_matrix.py [path/to/thesis.pdf]
With the PDF (MD5 5d111ff6d9a6717d14f2c265544406f1), the automatic label and value checks are run and recorded;
without it, the matrix records that they were not re-run.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parents[1] / 'data' / '02_historical_scoring'
sys.path.insert(0, str(ROOT))
from tools.annex1_transcription import ROWS, verify_against_pdf  # noqa: E402

FIELDS = ['claim_id', 'scope', 'claim', 'value_in_package', 'source_location', 'evidence_or_check', 'status',
          'correction_from_v1', 'notes']
# rows whose weight and label are verified but whose mapping onto the form (parent / response type) is inferred
INFERRED_STRUCTURE = {4: 'injury sub-question: no matching control on the Annex 2 screen',
                      7: 'injury sub-question: no matching control on the Annex 2 screen',
                      16: 'taken to be the Graves/Muy graves option of the threat-severity radio',
                      54: 'which I32 row corresponds to which of the two checkboxes is not printed',
                      55: 'which I32 row corresponds to which of the two checkboxes is not printed'}
OLD_ALIASES = {'I5_weapons_general': 'F02_weapons_used', 'I7_threats_general': 'F03_threats',
               'I17_criminal_history': 'F08_criminal_record'}
STATUS_HELP = {
    'verified': 'matches the primary source as printed',
    'corrected': 'version 1 differed from the source; version 2 follows the source',
    'inferred': 'follows from documented structure but is not stated explicitly',
    'assumption': 'the source is silent; a reconstruction choice, alternatives shown',
    'not_documented': 'not in the thesis; left open',
}


def annex_rows(pdf):
    cat = list(csv.DictReader(open(DATA / 'vpr4_0_annex1_indicators.csv', encoding='utf-8-sig')))
    old = list(csv.DictReader(open(DATA / 'version1_data' / 'vpr4_0_annex1_indicators_v1.csv',
                                   encoding='utf-8-sig')))
    pdf_report = {}
    if pdf:
        for r in verify_against_pdf(pdf):
            pdf_report[r['row']] = r['label_found_in_pdf_text']
    out = []
    for c, o, t in zip(cat, old, ROWS):
        row = int(c['row'])
        changes = []
        if o['code'] != c['code']:
            changes.append(f"code {o['code']} -> {c['code']}")
        if o['indicator'] != c['indicator']:
            changes.append(f"indicator number {o['indicator']} -> none (factor question)" if not c['indicator']
                           else f"indicator {o['indicator']} -> {c['indicator']}")
        if o['spanish_source_label'] != c['spanish_source_label']:
            changes.append(f"label '{o['spanish_source_label']}' -> '{c['spanish_source_label']}'")
        renamed_parent = ''
        if (o['parent_code'] or '') != c['parent_code']:
            if OLD_ALIASES.get(o['parent_code']) == c['parent_code']:
                renamed_parent = f"parent code renamed {o['parent_code']} -> {c['parent_code']} (same parent row)"
            else:
                changes.append(f"parent '{o['parent_code'] or 'none'}' -> '{c['parent_code'] or 'none'}'")
        if o['weight'] != c['weight']:
            changes.append(f"weight {o['weight']} -> {c['weight']}")
        if o['critical_indicator'] != c['critical_indicator']:
            changes.append(f"critical {o['critical_indicator']} -> {c['critical_indicator']}")
        ev = c['structure_evidence']
        structure_inferred = row in INFERRED_STRUCTURE
        if pdf:
            vals_ok = pdf_report.get(f"values p.{c['page']}")
            check = (f"label typed from page image; label {'found' if pdf_report[row] else 'NOT FOUND'} in PDF text of "
                     f"p. {c['page']}; right-column value sequence of p. {c['page']} {'matches' if vals_ok else 'DIFFERS'}")
        else:
            check = 'label and value typed from page image; automatic PDF check not re-run (no PDF given)'
        if c['critical_indicator'] == 'yes':
            check += f"; critical no. {c['critical_table1_number']} in Table 1 p. 193"
        status = 'corrected' if changes else ('inferred' if structure_inferred else 'verified')
        notes = '; '.join(x for x in (
            ('weight and label verified; form mapping inferred: ' + INFERRED_STRUCTURE[row]) if structure_inferred else '',
            renamed_parent) if x)
        out.append(dict(
            claim_id=f'A1-{row:02d}', scope='annex1_row',
            claim=f"Row {row}: {c['code']} ({c['english_label']})",
            value_in_package=(f"weight {c['weight']}; indicator {c['indicator'] or 'none'}; factor {c['factor']}; "
                              f"parent {c['parent_code'] or 'none'}; type {c['response_type']}; "
                              f"critical {c['critical_table1_number'] or 'no'}"),
            source_location=f"Annex 1 p. {c['page']} (label: \"{c['spanish_source_label']}\"); structure: {ev}",
            evidence_or_check=check, status=status, correction_from_v1='; '.join(changes), notes=notes))
    return out


CLAIMS = [
    # id, scope, claim, value, location, evidence, status, correction, notes
    ('S-01', 'source', 'Thesis PDF identity', 'lopez_ossorio_juan_jose.pdf, 336 pp., 7,345,382 bytes',
     'https://repositorio.uam.es/server/api/core/bitstreams/09c11ef0-a544-439a-a623-4e492db41610/content',
     'MD5 5d111ff6d9a6717d14f2c265544406f1 equals the checksum published by the UAM DSpace API', 'verified',
     'Version 1 had no access to the PDF and used a third-party transcription', 'Printed page numbers equal PDF page numbers'),
    ('S-02', 'source', 'Annex 1 counts', '63 rows; 39 I-numbers; 3 rows without I-number (10, 15, 38); 32 positive; 31 zero',
     'Annex 1 pp. 274-275', 'Counted on the page images', 'verified', '', ''),
    ('S-03', 'source', 'Sum of weights equals the stated maximum', '77.019', 'p. 194 ("de 0 a 77.019")',
     'Arithmetic; necessary but not sufficient (a transposition keeps the total)', 'verified', '', ''),
    ('S-04', 'source', 'Highest score observed in the construction data', '68.062', 'p. 194', 'Read on page', 'verified', '', ''),
    ('S-05', 'source', '13 critical indicators', 'rows 5, 8, 11, 19, 22, 23, 30, 33, 42, 43, 44, 60, 63; weights total 43.252',
     'Table 1 p. 193', 'Each Table 1 entry matched to one Annex 1 row by label', 'verified', '', ''),
    ('M-01', 'method', 'Weights are additive', 'score = sum of weights of rows answered Sí',
     'p. 193', '"de tipo actuarial con pesos aditivos ponderados ... todos los indicadores significativos suman"', 'verified', '', ''),
    ('M-02', 'method', 'Empirical weights are odds ratios for a new police report within four months',
     'criterion = reincidencia policial (new report, same aggressor), 4 months; construction sample 60% (n = 3,907) of 6,613',
     'pp. 160, 190-191', '"se estimo utilizar las OR obtenidas con la reincidencia de 4 meses (ver anexo 1)"', 'verified', '',
     'Not lethality, not a probability'),
    ('M-03', 'method', 'Critical indicators: expert weighting for homicide screening, doubled',
     'weight = 2 x initial value; I20 mental disorder fixed at 3', 'p. 192',
     '"ponderación experta para un screening del riesgo de homicidio"; "multiplicando por 2 su valor inicial, salvo trastorno mental ... puntuación directa de 3"',
     'verified', '', 'The initial (undoubled) values are not printed; the notebook counterfactual halves the published weights'),
    ('M-04', 'method', 'Two routes to a level', 'many low weights or few high weights', 'p. 192',
     '"mediante la suma de muchos indicadores con peso bajo y, también con la suma de menos indicadores de mayor peso"', 'verified', '', ''),
    ('M-05', 'method', 'Zero-weight rows retained to collect information', 'about 18 months', 'p. 196',
     '"El resto se van a mantener durante un periodo estimado de unos 18 meses con la finalidad de obtener más información"',
     'verified', '', ''),
    ('M-06', 'method', 'Answers are dichotomous; "no se sabe" treated as missing in the statistics', '', 'pp. 161, 164, 189',
     '"La categoría no se sabe fue considerada como valor perdido" (p. 161)', 'verified', '',
     'This is the statistical analysis, not the operational scoring rule'),
    ('M-07', 'method', 'How the operational software scored "No se sabe"', 'engine reports the range [all unknown = No, all unknown = Sí]',
     'not in the thesis', 'Searched Study 4 and Annexes 2, 5, 6', 'not_documented', 'Version 1 refused to score any incomplete form',
     'The bounds contain every possible rule because all weights are >= 0'),
    ('T-01', 'threshold', 'Cut-offs', '9.535 / 21.886 / 34.715 / 45.284', 'p. 194',
     '"no apreciado, de 0 hasta 9.535; bajo, hasta 21.886; medio, hasta 34.715; alto, hasta 45.284; y extremo, a partir del punto anterior"',
     'verified', '', ''),
    ('T-02', 'threshold', 'Criteria used to set the cut-offs', 'few false negatives at the first cut-off; serious cases from medio; workable proportions',
     'p. 194', '"que los clúster de riesgo mantuvieran unas proporciones asumibles desde el punto de vista de la seguridad"', 'verified', '', ''),
    ('T-03', 'threshold', 'Whether "hasta" includes the cut-off', 'read as <= (alternative available: upper_inclusive=False)',
     'p. 194', 'Every cut-off is exactly attainable by a consistent form (computed), so the reading matters', 'assumption', '',
     'At 45.284 the text overlaps ("alto, hasta 45.284" / "extremo, a partir del punto anterior")'),
    ('F-01', 'form', 'Sub-items are asked only when the parent is Sí', 'child Sí implies parent Sí; parent No closes children',
     'Annex 5 pp. 291-307', '"en caso afirmativo" throughout', 'verified', '', ''),
    ('F-02', 'form', 'Weapon, threat, control and life-problem types are multi-select', 'checkboxes, each added',
     'Annex 5 pp. 294, 295, 297, 301', '"Se pueden marcar varias opciones" / "permitiéndose señalar distintas opciones"', 'verified', '', ''),
    ('F-03', 'form', 'Firearm access (I6) is independent of weapon use (F02)', 'I6 has no parent', 'Annex 5 p. 295',
     '"independientemente de si empleó armas"', 'verified', '', ''),
    ('F-04', 'form', 'F08 criminal/police record is the parent of I17, I18, I19', 'parent F08', 'Annex 5 p. 301',
     '"en caso afirmativo, se debe especificar ... (Indicador 17) ... (Indicador 18) ... (Indicador 19)"', 'corrected',
     'I18 and I19 had no parent; row 38 was coded as I17', 'I18 alone: 4.012 (was 1.870)'),
    ('F-05', 'form', 'Severity is a radio Leve / Grave / Muy grave with one weighted row ("grave o muy grave")',
     'severity_option rows need their parent', 'Annex 2 pp. 276-277; Annex 5 pp. 292-294, 296', 'Screen images and coding instructions',
     'verified', '', 'For the threat block (row 16) the mapping to the radio is inferred'),
    ('F-06', 'form', 'No two weighted rows are mutually exclusive', 'full form attainable: 77.019', 'Annexes 2 and 5',
     'Follows from F-01 to F-05', 'inferred', '', ''),
    ('F-07', 'form', 'Officer coding guidance', 'choose the more severe level in doubt; raise severity if children present; infer I37',
     'Annex 5 pp. 292-296, 306', '"En caso de duda entre dos niveles, se recomienda indicar el nivel más grave"; I37 "en ningún caso podrá preguntarse"',
     'verified', '', ''),
    ('F-08', 'form', 'Annex 2 shows "Otros" options for F07 and F10 that have no Annex 1 row', 'not modelled', 'Annex 2 pp. 276-277',
     'Screen images', 'not_documented', '', 'Whether they were scored is unknown; Annex 1 gives them no weight row'),
    ('F-09', 'form', 'Factors F01 and F05 have no weight row of their own', 'not modelled as separate gates', 'Annex 1; Annex 2',
     'Compared factor list with Annex 1', 'inferred', '', 'Their indicators are answered directly'),
    ('P-01', 'procedure', 'Automatic level may be raised, never lowered, by officers', 'apply_officer_override',
     'Instrucción 7/2016, rule 1.5 (Annex 6 p. 327)', '"que podrá ser modificado por los agentes al alza"', 'verified', '',
     'Quoted from the thesis annex, not from the Boletín/official text'),
    ('P-02', 'procedure', 'Officers may inactivate "no apreciado" cases unless a judicial measure is in force',
     'procedural_consequences', 'rule 1.6 (Annex 6 p. 328)', '"los agentes pueden cambiar los casos a la situación de inactivos"', 'verified', '', ''),
    ('P-03', 'procedure', 'Victim informed at medio and above; result reported to the judicial authority',
     'procedural_consequences', 'rule 1.8 (Annex 6 p. 328)', '"Cuando el nivel de riesgo resulte medio, alto o extremo, se informará a la víctima"', 'verified', '', ''),
    ('P-04', 'procedure', 'Protection measures per level', 'not modelled', 'Adjunto I of the protocol', 'Not reproduced in the thesis',
     'not_documented', '', ''),
    ('E-01', 'evidence', 'Firearm use: 30 of 6,613 cases; RR 1.408 [.479-4.134], not significant; knife RR 1.845***',
     'used in notebook section 4 and app', 'Table 1 p. 163 (study of the predecessor form VPR2015; 6-month criterion)',
     'Read on page; crop in sources/02_historical_scoring/', 'verified', '', 'Explains the zero weight; says nothing about danger'),
    ('E-02', 'evidence', 'VPER4.0 manual adjustments', 'excluded from the model', 'pp. 198-199', 'Read on page', 'verified', '',
     'Companion follow-up form; cited only as an example of designer discretion'),
    ('C-01', 'computed', 'Most indicators while "no apreciado"', '25 of 39 indicators (27 facts), example score 9.165',
     'vpr4_historical.category_extremes / indicator_count_example', 'Exact dynamic programme over every consistent form',
     'inferred', 'Claimed "22 facts, 9.069" in earlier project notes', 'Logical possibility under the rule; not an observed case'),
    ('C-02', 'computed', 'Fewest indicators for "extremo"', '9 indicators (12 facts, 18 rows), example score 45.352',
     'vpr4_historical.indicator_count_example', 'Exact dynamic programme', 'inferred', '', ''),
    ('C-03', 'computed', 'Every cut-off exactly attainable', 'witness forms in exact_cutoff_examples()', 'vpr4_historical',
     'Exact enumeration of attainable scores (64,879)', 'inferred', 'Version 1 docstring said no score hits a cut-off', ''),
]


def main():
    pdf = sys.argv[1] if len(sys.argv) > 1 else None
    rows = annex_rows(pdf)
    rows += [dict(zip(FIELDS, c)) for c in CLAIMS]
    with open(DATA / 'SOURCE_VERIFICATION_MATRIX.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(len(rows), 'lines;', dict(Counter(r['status'] for r in rows)))


if __name__ == '__main__':
    main()
