"""Historical VPR4.0 scoring laboratory (López Ossorio, 2016). Version 2.

EDUCATIONAL HISTORICAL RECONSTRUCTION. NOT VioGén 2. NOT the operational VioGén software. Never use it to
assess a real person or to decide on protection.

What is documented in the thesis (UAM, 2016) and implemented here:
  * Annex 1, pp. 274-275: 63 weighted rows, 39 numbered indicators (I1-I39), 32 positive weights summing to 77.019.
  * p. 193: the instrument is "de tipo actuarial con pesos aditivos ponderados"; all significant indicators add up.
  * pp. 193-194: theoretical scale 0-77.019; empirical scale 0-68.062; cut-offs "no apreciado, de 0 hasta 9.535;
    bajo, hasta 21.886; medio, hasta 34.715; alto, hasta 45.284; y extremo, a partir del punto anterior".
  * Annex 2 (pp. 276-277) and Annex 5 (pp. 291-307): the form's structure. Sub-items are asked "en caso afirmativo"
    (child requires parent) and several are multi-select checkboxes ("se pueden marcar varias opciones").
  * Annex 6, Instrucción 7/2016, rule 1.5 (pp. 327-328): the system assigns the level automatically and officers may
    raise it ("al alza"), never lower it. Rule 1.6: "no apreciado" cases may be made inactive by officers when no
    judicial protection measure is in force.

What is NOT documented and is a reconstruction assumption here (see METHODS_AND_LIMITATIONS.md):
  * how the software scored "No se sabe" (unknown) answers. We never treat unknown as "No": we report the score range
    over every possible completion of the unknown answers (lower bound = unknown counted as No, upper bound = unknown
    counted as Sí). Because all weights are non-negative, any rule the software used lies inside that range.
  * the exact boundary semantics at a cut-off. We read "hasta" as <=. Every cut-off can be hit exactly by some
    consistent form (see threshold_attainability() and exact_cutoff_examples()), so the reading matters for a small
    number of forms. At 45.284 the text itself overlaps ("alto, hasta 45.284" / "extremo, a partir del punto
    anterior"); category(..., upper_inclusive=False) gives the alternative reading.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping

HERE = Path(__file__).resolve().parent
# In the standalone notebook the embedded catalogue sits beside this module.
CATALOG_PATH = HERE.parent.parent / 'data' / '02_historical_scoring' / 'vpr4_0_annex1_indicators.csv'
if not CATALOG_PATH.is_file():
    CATALOG_PATH = HERE / 'vpr4_0_annex1_indicators.csv'
STATUS = 'Historical VPR4.0 reconstruction (2016 thesis). Not VioGén 2; not the operational software.'

THRESHOLD_ROWS = (  # thesis p. 194
    ('No appreciable risk', Decimal('9.535')),
    ('Low', Decimal('21.886')),
    ('Medium', Decimal('34.715')),
    ('High', Decimal('45.284')),
    ('Extreme', None),
)
LEVEL_ES = {'No appreciable risk': 'No apreciado', 'Low': 'Bajo', 'Medium': 'Medio', 'High': 'Alto', 'Extreme': 'Extremo'}
LEVEL_ORDER = [label for label, _ in THRESHOLD_ROWS]
THEORETICAL_MAX = Decimal('77.019')   # p. 194
EMPIRICAL_MAX = Decimal('68.062')     # p. 194: highest score observed in the construction data

# Codes renamed in version 2 (the source rows carry no I-number of their own; see CHANGELOG.md)
OLD_CODE_ALIASES = {
    'I5_weapons_general': 'F02_weapons_used',
    'I7_threats_general': 'F03_threats',
    'I17_criminal_history': 'F08_criminal_record',
}


@dataclass(frozen=True)
class Item:
    row: int
    page: int
    code: str
    indicator: str          # I-number printed for the row ('' for the three factor questions F02, F03, F08)
    factor: str
    category: int
    spanish: str
    english: str
    weight: Decimal
    parent: str
    response_type: str
    critical: bool
    critical_no: int | None

    @property
    def milli(self) -> int:
        return int(self.weight * 1000)


def load_items(path: Path = CATALOG_PATH) -> tuple[Item, ...]:
    with open(path, encoding='utf-8-sig', newline='') as f:
        return tuple(Item(int(r['row']), int(r['page']), r['code'], r['indicator'], r['factor'], int(r['category']),
                          r['spanish_source_label'], r['english_label'], Decimal(r['weight']), r['parent_code'],
                          r['response_type'], r['critical_indicator'] == 'yes',
                          int(r['critical_table1_number']) if r['critical_table1_number'] else None)
                     for r in csv.DictReader(f))


ITEMS = load_items()
BY_CODE = {it.code: it for it in ITEMS}
CHILDREN: dict[str, list[str]] = {}
for _it in ITEMS:
    if _it.parent:
        CHILDREN.setdefault(_it.parent, []).append(_it.code)
assert len(ITEMS) == 63 and len(BY_CODE) == 63
assert sum(x.weight for x in ITEMS) == THEORETICAL_MAX
assert all(BY_CODE[p].parent == '' for p in CHILDREN), 'only one level of nesting is documented'


# --------------------------------------------------------------------------- input handling
def _resolve(answers: Mapping[str, bool | None]) -> dict[str, bool | None]:
    out: dict[str, bool | None] = {}
    for code, value in answers.items():
        code = OLD_CODE_ALIASES.get(code, code)
        if code not in BY_CODE:
            raise KeyError(f'Unknown indicator code: {code}')
        if value is not True and value is not False and value is not None:
            raise TypeError(f'Answer {code} must be True (Sí), False (No) or None (No se sabe / not recorded)')
        out[code] = value
    return out


def normalize(answers: Mapping[str, bool | None]) -> tuple[dict[str, bool | None], dict[str, list[str]]]:
    """Apply the form's documented structure. Returns (answers for all 63 rows, notes).

    * A row absent from the input is unknown (None), never "No".
    * A sub-item answered Sí implies its parent question is Sí (sub-items are asked "en caso afirmativo").
    * A sub-item answered Sí under a parent answered No is inconsistent and raises ValueError.
    * When a parent is No, its sub-items are not asked: they are set to No and listed as not applicable.
    """
    given = _resolve(answers)
    out: dict[str, bool | None] = {it.code: given.get(it.code) for it in ITEMS}
    notes = {'parent_implied': [], 'not_applicable': [], 'absent_from_input': [c for c in BY_CODE if c not in given]}
    bad = [c for c, v in out.items() if v is True and BY_CODE[c].parent and out[BY_CODE[c].parent] is False]
    if bad:
        raise ValueError(f'Sub-item answered Sí while its parent question is No: {bad}')
    for code, v in list(out.items()):
        p = BY_CODE[code].parent
        if v is True and p and out[p] is not True:
            out[p] = True
            notes['parent_implied'].append(p)
    for parent, kids in CHILDREN.items():
        if out[parent] is False:
            for k in kids:
                if out[k] is None:
                    notes['not_applicable'].append(k)
                out[k] = False
    return out, notes


def empty_case() -> dict[str, bool]:
    """Fully specified hypothetical form with every row answered No (not an absence-of-evidence inference)."""
    return {it.code: False for it in ITEMS}


def make_case(*positive_codes: str, unknown: Iterable[str] = ()) -> dict[str, bool | None]:
    """Fully specified hypothetical form: listed codes Sí, `unknown` codes No se sabe, every other row No."""
    case: dict[str, bool | None] = empty_case()
    for code in positive_codes:
        code = OLD_CODE_ALIASES.get(code, code)
        if code not in BY_CODE:
            raise KeyError(f'Unknown indicator: {code}')
        case[code] = True
    for code in unknown:
        code = OLD_CODE_ALIASES.get(code, code)
        if code not in BY_CODE:
            raise KeyError(f'Unknown indicator: {code}')
        case[code] = None
    # parents of selected sub-items are Sí; parents of unknown sub-items cannot be No
    for code in list(case):
        p = BY_CODE[code].parent
        if p and case[code] is True:
            case[p] = True
        elif p and case[code] is None and case[p] is False:
            case[p] = None
    return case


# --------------------------------------------------------------------------- scoring
def category(score: Decimal | str | float, upper_inclusive: bool = True) -> str:
    """Category for an additive score. Default reads "hasta X" (p. 194) as <= X; upper_inclusive=False gives
    the alternative reading (a score exactly at a cut-off goes to the higher level)."""
    val = Decimal(str(score))
    if val < 0 or val > THEORETICAL_MAX:
        raise ValueError('A VPR4.0 additive score lies between 0 and 77.019')
    for label, upper in THRESHOLD_ROWS:
        if upper is None or (val <= upper if upper_inclusive else val < upper):
            return label
    raise AssertionError('unreachable')


def _upper_completion(norm: Mapping[str, bool | None]) -> dict[str, bool]:
    up = {c: (v is not False) for c, v in norm.items()}
    for code, it in BY_CODE.items():          # a sub-item can only be Sí if its parent can be Sí
        if it.parent and not up[it.parent]:
            up[code] = False
    return up


def evaluate(answers: Mapping[str, bool | None]) -> dict:
    """Score a hypothetical form.

    score_min / score_max bound the additive score over every completion of the unknown answers.
    `category` is given only when nothing is unknown; `category_at_min` / `category_at_max` give the level at each
    bound, and `category_robust_to_unknowns` says whether they agree.
    """
    norm, notes = normalize(answers)
    lo = sum((BY_CODE[c].weight for c, v in norm.items() if v is True), Decimal('0'))
    up = _upper_completion(norm)
    hi = sum((BY_CODE[c].weight for c, v in up.items() if v), Decimal('0'))
    unknown = [c for c, v in norm.items() if v is None]
    selected = [BY_CODE[c] for c, v in norm.items() if v is True]
    contributions = [dict(code=it.code, indicator=it.indicator or it.factor, label=it.english, weight=float(it.weight),
                          critical=it.critical, page=it.page) for it in selected]
    cat_lo, cat_hi = category(lo), category(hi)
    return dict(
        status=STATUS,
        complete=not unknown,
        score=float(lo), score_exact=str(lo),
        score_min=float(lo), score_max=float(hi),
        category=cat_lo if not unknown else None,
        category_es=LEVEL_ES[cat_lo] if not unknown else None,
        category_at_min=cat_lo, category_at_max=cat_hi,
        category_robust_to_unknowns=cat_lo == cat_hi,
        unknown_count=len(unknown), unknown_codes=unknown,
        unknown_weight_at_stake=float(hi - lo),
        contributions=contributions,
        positive_rows=[c['code'] for c in contributions if c['weight'] > 0],
        zero_weight_positive=[c['code'] for c in contributions if c['weight'] == 0],
        indicators_present=sorted({it.indicator for it in selected if it.indicator}, key=lambda s: int(s[1:])),
        factor_questions_yes=sorted({it.code for it in selected if not it.indicator}),
        critical_present=[it.code for it in selected if it.critical],
        notes=notes,
        interpretation=('Historical hypothetical classification under the documented additive rule' if not unknown else
                        'Some answers unknown: the category is not determined; see score_min/score_max'),
    )


def compare_cases(case_a: Mapping[str, bool | None], case_b: Mapping[str, bool | None]) -> dict:
    a, b = evaluate(case_a), evaluate(case_b)
    if not a['complete'] or not b['complete']:
        raise ValueError('Comparisons require fully specified hypothetical forms')
    na, nb = normalize(case_a)[0], normalize(case_b)[0]
    diffs = [dict(code=it.code, label=it.english, before=na[it.code], after=nb[it.code], weight=float(it.weight))
             for it in ITEMS if na[it.code] != nb[it.code]]
    return dict(before=a, after=b, delta=float(Decimal(b['score_exact']) - Decimal(a['score_exact'])), changes=diffs)


# --------------------------------------------------------------------------- procedure (Instrucción 7/2016, Annex 6)
def apply_officer_override(automatic: str, officer_choice: str) -> dict:
    """Rule 1.5 of Instrucción 7/2016 (thesis pp. 327-328): the level assigned automatically by VioGén "podrá ser
    modificado por los agentes al alza" when indications not reflected in the indicators make it necessary.
    A downward change is not provided for and is rejected."""
    if automatic not in LEVEL_ORDER or officer_choice not in LEVEL_ORDER:
        raise ValueError(f'Levels must be one of {LEVEL_ORDER}')
    i, j = LEVEL_ORDER.index(automatic), LEVEL_ORDER.index(officer_choice)
    if j < i:
        raise ValueError('Instrucción 7/2016, rule 1.5, allows officers to change the automatic level upwards only')
    return dict(automatic=automatic, final=officer_choice, raised_by_officer=j > i, steps_raised=j - i,
                rule='Instrucción 7/2016, rule 1.5 (thesis Annex 6, pp. 327-328)')


def procedural_consequences(level: str, judicial_protection_in_force: bool | None = None) -> list[str]:
    """What Instrucción 7/2016 (rules 1.6 and 1.8, thesis p. 328) attaches to a level. Police protection measures
    per level are in the protocol's Adjunto I catalogues, which are not reproduced in the thesis."""
    if level not in LEVEL_ORDER:
        raise ValueError(level)
    out = []
    if level == 'No appreciable risk':
        if judicial_protection_in_force:
            out.append('Rule 1.6: the case stays active because a judicial protection measure is in force.')
        else:
            out.append('Rule 1.6: officers MAY switch the case to inactive (discretionary: "pueden"), '
                       'unless a judicial protection measure is in force.')
    else:
        out.append('Rule 1.6: the case stays active (unless e.g. death or departure abroad makes it pointless).')
    if level in ('Medium', 'High', 'Extreme'):
        out.append('Rule 1.8: the victim is informed of the level (Ley 4/2015, Estatuto de la víctima).')
    out.append('Rule 1.8: the result is reported to the judicial authority with the main risk factors.')
    out.append('Rule 2.1: each level carries police protection measures from the Adjunto I catalogues (not in the thesis).')
    return out


# --------------------------------------------------------------------------- structural analysis (exact, combinatorial)
def _groups() -> list[list[Item]]:
    """Rows that must be decided together: a parent with its sub-items; rows sharing an I-number otherwise."""
    groups: dict[str, list[Item]] = {}
    for it in ITEMS:
        root = it.parent or it.code
        key = root if (root in CHILDREN) else (it.indicator or it.code)
        groups.setdefault(key, []).append(it)
    return list(groups.values())


def _facts(codes) -> tuple[set[str], set[str]]:
    """Indicators (I1-I39) present, and 'facts' = indicators plus factor questions (F02, F03, F08) answered Sí."""
    inds = {BY_CODE[c].indicator for c in codes if BY_CODE[c].indicator}
    return inds, inds | {c for c in codes if not BY_CODE[c].indicator}


def _group_options(group: list[Item]) -> list[tuple[int, int, int, int]]:
    """Every consistent Sí/No assignment of a group: (milli-points, rows Sí, indicators, facts)."""
    from itertools import product
    opts = set()
    for bits in product((False, True), repeat=len(group)):
        on = {it.code for it, b in zip(group, bits) if b}
        if any(BY_CODE[c].parent and BY_CODE[c].parent not in on for c in on):
            continue
        inds, facts = _facts(on)
        opts.add((sum(BY_CODE[c].milli for c in on), len(on), len(inds), len(facts)))
    return sorted(opts)


@lru_cache(maxsize=None)
def _frontier() -> dict[int, tuple[int, ...]]:
    """For every attainable score (milli-points): min/max rows, min/max indicators, min/max facts."""
    state: dict[int, tuple[int, ...]] = {0: (0, 0, 0, 0, 0, 0)}
    for g in _groups():
        nxt: dict[int, tuple[int, ...]] = {}
        for s, v in state.items():
            for w, nrows, k, nf in _group_options(g):
                cand = (v[0] + nrows, v[1] + nrows, v[2] + k, v[3] + k, v[4] + nf, v[5] + nf)
                cur = nxt.get(s + w)
                nxt[s + w] = cand if cur is None else tuple(min(a, b) if i % 2 == 0 else max(a, b)
                                                            for i, (a, b) in enumerate(zip(cur, cand)))
        state = nxt
    return state


def attainable_scores() -> list[Decimal]:
    return [Decimal(m) / 1000 for m in sorted(_frontier())]


def threshold_attainability() -> list[dict]:
    """Can a consistent form score exactly a cut-off? If not, "<=" versus "<" cannot matter."""
    f = _frontier()
    out = []
    for label, upper in THRESHOLD_ROWS[:-1]:
        m = int(upper * 1000)
        below = max(s for s in f if s <= m)
        above = min(s for s in f if s > m)
        out.append(dict(cutoff=str(upper), level_up_to_cutoff=label, exactly_attainable=m in f,
                        nearest_score_below=str(Decimal(below) / 1000), nearest_score_above=str(Decimal(above) / 1000)))
    return out


def category_extremes() -> list[dict]:
    """For each level: the fewest indicators that can produce it and the most indicators it can contain."""
    f = _frontier()
    out = []
    bounds = [Decimal('0')] + [u for _, u in THRESHOLD_ROWS[:-1]] + [THEORETICAL_MAX]
    for i, (label, _) in enumerate(THRESHOLD_ROWS):
        lo_m = 0 if i == 0 else int(bounds[i] * 1000) + 1
        hi_m = int(bounds[i + 1] * 1000)
        inside = {s: v for s, v in f.items() if lo_m <= s <= hi_m}
        out.append(dict(level=label, attainable_scores=len(inside),
                        min_indicators=min(v[2] for v in inside.values()), max_indicators=max(v[3] for v in inside.values()),
                        min_facts=min(v[4] for v in inside.values()), max_facts=max(v[5] for v in inside.values()),
                        min_rows=min(v[0] for v in inside.values()), max_rows=max(v[1] for v in inside.values())))
    return out


@lru_cache(maxsize=None)
def _witnesses() -> dict[int, tuple[str, ...]]:
    """One consistent form (fewest Sí rows) for every attainable score."""
    from itertools import product
    best: dict[int, tuple[str, ...]] = {0: ()}
    for g in _groups():
        nxt: dict[int, tuple[str, ...]] = {}
        for s, codes in best.items():
            for bits in product((False, True), repeat=len(g)):
                on = tuple(it.code for it, b in zip(g, bits) if b)
                if any(BY_CODE[c].parent and BY_CODE[c].parent not in on for c in on):
                    continue
                w = s + sum(BY_CODE[c].milli for c in on)
                if w not in nxt or len(codes) + len(on) < len(nxt[w]):
                    nxt[w] = codes + on
        best = nxt
    return best


def exact_cutoff_examples() -> list[dict]:
    """A consistent hypothetical form scoring exactly each cut-off (so the boundary reading matters)."""
    w = _witnesses()
    out = []
    for label, upper in THRESHOLD_ROWS[:-1]:
        codes = w[int(upper * 1000)]
        out.append(dict(cutoff=str(upper), codes=list(codes), inclusive_reading=category(upper),
                        exclusive_reading=category(upper, upper_inclusive=False)))
    return out


def _level_bounds_milli(level: str) -> tuple[int, int]:
    i = LEVEL_ORDER.index(level)
    lo = 0 if i == 0 else int(THRESHOLD_ROWS[i - 1][1] * 1000) + 1
    up = THRESHOLD_ROWS[i][1]
    return lo, int((up if up is not None else THEORETICAL_MAX) * 1000)


def indicator_count_example(level: str = 'No appreciable risk', most: bool = True) -> dict:
    """A concrete consistent form in `level` holding the MOST (most=True) or the FEWEST (most=False) indicators
    I1-I39. Exact dynamic programme over the form's groups (indicator count is additive across groups); ties are
    broken towards the lowest score (most=True) or the fewest rows answered Sí (most=False). Shows logical possibility under the documented form
    structure only: it says nothing about how often, or whether, such forms occurred."""
    from itertools import product
    lo, hi = _level_bounds_milli(level)
    sign = 1 if most else -1
    best: dict[int, tuple[int, tuple[str, ...]]] = {0: (0, ())}
    for g in _groups():
        nxt: dict[int, tuple[int, tuple[str, ...]]] = {}
        for s, (k, codes) in best.items():
            for bits in product((False, True), repeat=len(g)):
                on = tuple(it.code for it, b in zip(g, bits) if b)
                if any(BY_CODE[c].parent and BY_CODE[c].parent not in on for c in on):
                    continue
                w = s + sum(BY_CODE[c].milli for c in on)
                if w > hi:
                    continue
                cand = (k + len({BY_CODE[c].indicator for c in on if BY_CODE[c].indicator}), codes + on)
                cur = nxt.get(w)
                if cur is None or (sign * cand[0], -len(cand[1])) > (sign * cur[0], -len(cur[1])):
                    nxt[w] = cand
        best = nxt
    pool = [(k, s, codes) for s, (k, codes) in best.items() if lo <= s <= hi]
    if most:   # most indicators, then the lowest score, then fewest rows
        k, s, codes = min(pool, key=lambda t: (-t[0], t[1], len(t[2])))
    else:      # fewest indicators, then fewest rows, then the lowest score
        k, s, codes = min(pool, key=lambda t: (t[0], len(t[2]), t[1]))
    ext = next(e for e in category_extremes() if e['level'] == level)
    assert k == (ext['max_indicators'] if most else ext['min_indicators'])
    ev = evaluate(make_case(*codes))
    assert ev['category'] == level
    inds, facts = _facts(codes)
    return dict(level=level, most=most, indicators=k, facts=len(facts), rows_yes=len(codes), codes=list(codes),
                evaluation=ev)


def max_indicators_example(level: str = 'No appreciable risk') -> dict:
    """Kept for compatibility: the form in `level` with the most indicators (see indicator_count_example)."""
    return indicator_count_example(level, most=True)


def source_integrity() -> dict:
    w = [x.weight for x in ITEMS]
    return dict(main_indicators=len({x.indicator for x in ITEMS if x.indicator}), item_rows=len(ITEMS),
                factor_question_rows=sum(1 for x in ITEMS if not x.indicator), positive_rows=sum(v > 0 for v in w),
                zero_rows=sum(v == 0 for v in w), critical_items=sum(x.critical for x in ITEMS),
                critical_numbers=sorted(x.critical_no for x in ITEMS if x.critical),
                theoretical_ceiling=str(sum(w)), reported_ceiling=str(THEORETICAL_MAX),
                critical_weight_total=str(sum(x.weight for x in ITEMS if x.critical)),
                max_attainable_under_form_structure=str(attainable_scores()[-1]))


if __name__ == '__main__':
    import json
    print(json.dumps(source_integrity(), indent=2))
    print(json.dumps(threshold_attainability(), indent=2))
    print(json.dumps(category_extremes(), indent=2))
    for label, case in [('Firearm', make_case('I5_firearm_use')), ('Knife', make_case('I5_knife'))]:
        e = evaluate(case)
        print(label, e['score_exact'], e['category'])
