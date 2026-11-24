"""Engine tests: documented rules, reconstruction assumptions and regressions for every version-2 correction."""
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest  # noqa: E402

import vpr4_historical as V  # noqa: E402
from vpr4_historical import (BY_CODE, CHILDREN, ITEMS, apply_officer_override, category, compare_cases,  # noqa: E402
                             empty_case, evaluate, make_case, procedural_consequences, source_integrity)


# ---------------------------------------------------------------- source counts (Annex 1, Table 1, p. 194)
def test_catalog_counts():
    x = source_integrity()
    assert x['main_indicators'] == 39          # I1-I39
    assert x['item_rows'] == 63
    assert x['factor_question_rows'] == 3      # F02, F03, F08: rows without an I-number in Annex 1
    assert x['positive_rows'] == 32 and x['zero_rows'] == 31
    assert x['critical_items'] == 13 and x['critical_numbers'] == list(range(1, 14))
    assert x['theoretical_ceiling'] == '77.019'
    assert x['max_attainable_under_form_structure'] == '77.019'


def test_every_row_has_page_and_known_type():
    for it in ITEMS:
        assert it.page in (274, 275)
        assert it.response_type in {'gate_question', 'indicator', 'severity_option', 'subtype_checkbox', 'sub_question'}
        assert it.factor in {f'F{n:02d}' for n in range(1, 13)}


# ---------------------------------------------------------------- structure (Annexes 2 and 5)
def test_criminal_record_question_is_parent_of_i17_i18_i19():
    # Annex 5 p. 301: "en caso afirmativo, se debe especificar ... (Indicador 17) ... (18) ... (19)"
    assert sorted(CHILDREN['F08_criminal_record']) == ['I17_prior_breaches', 'I18_prior_aggression',
                                                       'I19_prior_ipv_other_partners']
    assert BY_CODE['F08_criminal_record'].indicator == ''


def test_firearm_access_is_independent_of_weapon_use():
    # Annex 5 p. 295: "independientemente de si empleó armas"
    assert BY_CODE['I6_firearm_access'].parent == ''


def test_weapon_subtypes_are_multiselect():
    # Annex 5 p. 294: "Se pueden marcar varias opciones"
    e = evaluate(make_case('I5_knife', 'I5_firearm_use', 'I5_other_object'))
    assert e['score_exact'] == '5.533'


def test_only_one_level_of_nesting():
    assert all(BY_CODE[p].parent == '' for p in CHILDREN)


# ---------------------------------------------------------------- normalisation
def test_child_implies_parent():
    e = evaluate(make_case('I18_prior_aggression'))
    assert e['score_exact'] == '4.012'                     # 2.142 + 1.870 (version 1 gave 1.870)
    assert 'F08_criminal_record' in e['factor_questions_yes']


def test_child_yes_parent_no_is_rejected():
    case = empty_case()
    case['I5_knife'] = True
    case['F02_weapons_used'] = False
    with pytest.raises(ValueError):
        evaluate(case)


def test_parent_no_closes_unknown_children():
    case = {it.code: None for it in ITEMS}
    case['F02_weapons_used'] = False
    norm, notes = V.normalize(case)
    assert norm['I5_knife'] is False and 'I5_knife' in notes['not_applicable']


def test_old_codes_still_accepted():
    assert evaluate(make_case('I5_weapons_general'))['score_exact'] == '1.533'
    assert evaluate(make_case('I17_criminal_history'))['score_exact'] == '2.142'


def test_reject_bad_input():
    with pytest.raises(KeyError):
        evaluate({'invalid_code': True})
    with pytest.raises(TypeError):
        evaluate({'I5_knife': 'yes'})
    with pytest.raises(ValueError):
        category(100)


# ---------------------------------------------------------------- scoring and thresholds (p. 194)
def test_extremes():
    assert evaluate(empty_case())['category'] == 'No appreciable risk'
    full = evaluate(make_case(*BY_CODE))
    assert full['score_exact'] == '77.019' and full['category'] == 'Extreme'


@pytest.mark.parametrize('score,level', [('9.535', 'No appreciable risk'), ('9.536', 'Low'), ('21.886', 'Low'),
                                         ('21.887', 'Medium'), ('34.715', 'Medium'), ('34.716', 'High'),
                                         ('45.284', 'High'), ('45.285', 'Extreme')])
def test_cutoffs_inclusive_reading(score, level):
    assert category(score) == level


def test_cutoffs_exclusive_reading():
    assert category('9.535', upper_inclusive=False) == 'Low'
    assert category('45.284', upper_inclusive=False) == 'Extreme'


def test_every_cutoff_is_exactly_attainable():
    rows = V.threshold_attainability()
    assert all(r['exactly_attainable'] for r in rows)
    for ex in V.exact_cutoff_examples():
        assert evaluate(make_case(*ex['codes']))['score_exact'] == ex['cutoff']
        assert ex['inclusive_reading'] != ex['exclusive_reading']


# ---------------------------------------------------------------- unknown answers ("No se sabe")
def test_unknown_is_never_no():
    e = evaluate({'I5_firearm_use': True})          # every other row absent = unknown
    assert e['complete'] is False and e['category'] is None
    assert e['score_min'] == 1.533 and e['score_max'] == 77.019


def test_unknown_bounds_and_robustness():
    e = evaluate(make_case('I11_stalking', 'I36_recent_separation', unknown=['I39_victim_fear_lethal', 'I9_jealousy']))
    assert (e['score_min'], e['score_max']) == (8.226, 14.596)
    assert e['category_at_min'] == 'No appreciable risk' and e['category_at_max'] == 'Low'
    assert e['category_robust_to_unknowns'] is False
    e2 = evaluate(make_case('I5_knife', unknown=['I10_control_cyber']))
    assert e2['category_robust_to_unknowns'] is True     # 5.533 to 9.295, both No apreciado


def test_unknown_child_under_unknown_parent_counts_both_in_upper_bound():
    e = evaluate(make_case(unknown=['I5_knife']))
    assert e['score_max'] == 5.533 and e['score_min'] == 0.0


# ---------------------------------------------------------------- research claims
def test_firearm_versus_knife():
    x = compare_cases(make_case('I5_firearm_use'), make_case('I5_knife'))
    assert x['before']['score_exact'] == '1.533' and x['after']['score_exact'] == '5.533'
    assert x['delta'] == 4.0
    assert BY_CODE['I5_knife'].critical and BY_CODE['I5_knife'].critical_no == 3
    assert not BY_CODE['I5_firearm_use'].critical


def test_stalking_separation_examples():
    assert evaluate(make_case('I11_stalking', 'I36_recent_separation'))['score_exact'] == '8.226'
    e = evaluate(make_case('I11_stalking', 'I36_recent_separation', 'I39_victim_fear_lethal'))
    assert e['score_exact'] == '11.056' and e['category'] == 'Low'


def test_input_coding_choice_crosses_first_cutoff():
    a = evaluate(make_case('I11_stalking', 'I36_recent_separation'))
    b = evaluate(make_case('I11_stalking', 'I36_recent_separation', 'I1_psychological'))
    assert a['category'] == 'No appreciable risk' and b['category'] == 'Low'


def test_zero_weight_rows_do_not_move_score():
    e = evaluate(make_case('I6_firearm_access', 'I24_disability', 'I25_pregnancy', 'I28_social_support'))
    assert e['score'] == 0.0 and len(e['zero_weight_positive']) == 4


def test_most_indicators_still_no_appreciable():
    ext = {r['level']: r for r in V.category_extremes()}
    assert ext['No appreciable risk']['max_indicators'] == 25
    m = V.max_indicators_example()
    assert m['indicators'] == 25 and m['evaluation']['category'] == 'No appreciable risk'
    assert Decimal(m['evaluation']['score_exact']) <= Decimal('9.535')
    # the composition quoted in the notebook (section 6): violence recorded as leve, weapon object, threats to children
    assert {'I2_physical', 'I3_sexual', 'I5_other_object', 'I7_children_threat', 'I25_pregnancy', 'I34_dependents'} <= set(m['codes'])
    assert m['evaluation']['score_exact'] == '9.165'


def test_fewest_indicators_for_extreme():
    m = V.indicator_count_example('Extreme', most=False)
    assert m['indicators'] == 9 and m['facts'] == 12 and m['rows_yes'] == 18
    assert m['evaluation']['category'] == 'Extreme'
    assert 'F08_criminal_record' in m['codes']           # a weighted factor question that is not an I-number


def test_low_reachable_with_one_indicator_because_gates_carry_weight():
    m = V.indicator_count_example('Low', most=False)
    assert m['indicators'] == 1 and {'F02_weapons_used', 'F08_criminal_record'} <= set(m['codes'])


def test_two_routes_to_a_level():
    # p. 192: a level can be reached with many low-weight indicators or with fewer high-weight ones
    ext = {r['level']: r for r in V.category_extremes()}
    assert ext['Extreme']['min_indicators'] < ext['Extreme']['max_indicators']
    assert ext['High']['min_indicators'] <= 6 < 30 <= ext['High']['max_indicators']


def test_critical_weight_share():
    assert source_integrity()['critical_weight_total'] == '43.252'


# ---------------------------------------------------------------- procedure (Instrucción 7/2016, Annex 6)
def test_override_upwards_only():
    assert apply_officer_override('Low', 'High')['steps_raised'] == 2
    assert apply_officer_override('Low', 'Low')['raised_by_officer'] is False
    with pytest.raises(ValueError):
        apply_officer_override('High', 'Low')


def test_procedural_consequences():
    na = ' '.join(procedural_consequences('No appreciable risk'))
    assert 'MAY switch the case to inactive' in na
    assert 'stays active' in ' '.join(procedural_consequences('No appreciable risk', judicial_protection_in_force=True))
    assert 'victim is informed' in ' '.join(procedural_consequences('Medium'))
    assert 'victim is informed' not in ' '.join(procedural_consequences('Low'))


# ---------------------------------------------------------------- scenario regression
def test_scenarios_file_matches_engine():
    import json
    rows = json.loads((Path(__file__).resolve().parents[3] / 'data' / '02_historical_scoring' / 'hypothetical_scenarios.json').read_text(encoding='utf-8'))
    for r in rows:
        e = evaluate(make_case(*r['selected_rows'], unknown=r['unknown_rows']))
        assert (e['score_min'], e['score_max']) == (r['score_min'], r['score_max']), r['name']
