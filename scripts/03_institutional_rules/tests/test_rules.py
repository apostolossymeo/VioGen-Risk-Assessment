"""Engine tests: one or more tests per documented branch, plus the cases where the answer must be "unknown"."""
import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from decision_rules import (LEVELS, Scenario, assessment_instrument, case_status_rule, enumerate_abstract_pathways,  # noqa: E402
                            exceptional_inactivation, first_vper, later_vper, ordinary_inactivation, permitted_officer_levels,
                            protection_floor, reactivation, supervision, trace, validate, vper_court_notification)

S = Scenario


# ------------------------------------------------------------------------------------------- levels and override
def test_levels():
    assert LEVELS[2019] == ('no_appreciable', 'low', 'medium', 'high', 'extreme')
    assert LEVELS[2025] == ('low', 'medium', 'high', 'extreme')


@pytest.mark.parametrize('bad', [dict(version=2020, algorithm_category='low'), dict(version=2025, algorithm_category='no_appreciable'),
                                 dict(version=2019, algorithm_category='medium', officer_category='low'),
                                 dict(version=2025, algorithm_category='high', officer_category='medium'),
                                 dict(version=2019, algorithm_category='low', case_status='supervised'),
                                 dict(version=2025, algorithm_category='low', case_status='closed')])
def test_invalid_inputs_raise(bad):
    with pytest.raises(ValueError):
        validate(S(**bad))


def test_upward_only_both_years():
    assert permitted_officer_levels(2019, 'low') == ('low', 'medium', 'high', 'extreme')
    assert permitted_officer_levels(2025, 'high') == ('high', 'extreme')
    assert trace(S(2025, 'medium', 'extreme'))['override'] == 'raised'


# ------------------------------------------------------------------------------------------- first VPER
@pytest.mark.parametrize('level', ['low', 'medium', 'high', 'extreme'])
def test_2019_first_vper_seven_days_for_bajo_and_above(level):
    r = first_vper(S(2019, level, first_vper_done=False))
    assert (r['status'], r['max_days'], r['min_days']) == ('applies', 7, None)


def test_2019_no_apreciado_first_vper_depends_on_measures():
    assert first_vper(S(2019, 'no_appreciable', judicial_measures=True, first_vper_done=False))['max_days'] == 7
    assert first_vper(S(2019, 'no_appreciable', judicial_measures=False, first_vper_done=False))['status'] == 'not_stated'
    assert first_vper(S(2019, 'no_appreciable', judicial_measures=None, first_vper_done=False))['status'] == 'cannot_determine'


@pytest.mark.parametrize('level', ['no_appreciable', 'low', 'extreme'])
def test_2019_special_relevance_is_a_minimum_wait_any_level(level):
    r = first_vper(S(2019, level, special_relevance=True, first_vper_done=False))
    assert (r['min_days'], r['max_days']) == (7, None)


@pytest.mark.parametrize('level', ['medium', 'high', 'extreme'])
def test_2025_first_vper_fifteen_days(level):
    assert first_vper(S(2025, level, first_vper_done=False))['max_days'] == 15


def test_2025_bajo_first_vper():
    assert first_vper(S(2025, 'low', judicial_measures=True, first_vper_done=False))['max_days'] == 15
    r = first_vper(S(2025, 'low', judicial_measures=False, first_vper_done=False))
    assert r['status'] == 'not_stated' and r['max_days'] is None
    assert first_vper(S(2025, 'low', judicial_measures=None, first_vper_done=False))['status'] == 'cannot_determine'


@pytest.mark.parametrize('level', ['medium', 'high'])
def test_2025_special_relevance_minimum_for_medio_alto(level):
    r = first_vper(S(2025, level, special_relevance=True, first_vper_done=False))
    assert (r['status'], r['min_days'], r['max_days']) == ('applies', 7, None)


def test_2025_special_relevance_extremo_may_be_earlier():
    r = first_vper(S(2025, 'extreme', special_relevance=True, first_vper_done=False))
    assert (r['status'], r['min_days'], r['max_days']) == ('requires_judgement', None, 15)


def test_2025_special_relevance_bajo_falls_under_general_rule():
    assert first_vper(S(2025, 'low', special_relevance=True, judicial_measures=True, first_vper_done=False))['max_days'] == 15


@pytest.mark.parametrize('kw,status', [(dict(case_status='inactive'), 'not_applicable'), (dict(case_status=None), 'cannot_determine'),
                                       (dict(known_new_incident=True), 'not_applicable'), (dict(known_new_incident=None), 'cannot_determine'),
                                       (dict(special_relevance=None), 'cannot_determine'), (dict(first_vper_done=True), 'not_applicable')])
def test_first_vper_prerequisites(kw, status):
    for y in (2019, 2025):
        r = first_vper(S(y, 'medium', **{'first_vper_done': False, **kw}))
        assert r['status'] == status and r['max_days'] is None


# ------------------------------------------------------------------------------------------- later VPER
@pytest.mark.parametrize('year,level,value,unit', [(2019, 'extreme', 72, 'hours'), (2019, 'high', 7, 'days'), (2019, 'medium', 30, 'days'),
                                                   (2019, 'low', 60, 'days'), (2019, 'no_appreciable', 90, 'days'),
                                                   (2025, 'extreme', 72, 'hours'), (2025, 'high', 7, 'days'), (2025, 'medium', 30, 'days')])
def test_later_vper_intervals(year, level, value, unit):
    r = later_vper(S(year, level, first_vper_done=True))
    assert (r['value'], r['unit'], r['bound']) == (value, unit, 'strictly_before')


def test_2025_bajo_later_interval_depends_on_measures():
    assert later_vper(S(2025, 'low', judicial_measures=True, first_vper_done=True))['value'] == 60
    assert later_vper(S(2025, 'low', judicial_measures=False, first_vper_done=True))['value'] == 90
    assert later_vper(S(2025, 'low', judicial_measures=None, first_vper_done=True))['status'] == 'cannot_determine'


def test_2019_bajo_interval_does_not_depend_on_measures():
    assert {later_vper(S(2019, 'low', judicial_measures=jm, first_vper_done=True))['value'] for jm in (True, False)} == {60}


@pytest.mark.parametrize('kw,status', [(dict(first_vper_done=None), 'cannot_determine'), (dict(first_vper_done=False), 'not_applicable'),
                                       (dict(case_status='inactive'), 'not_applicable'), (dict(case_status=None), 'cannot_determine'),
                                       (dict(known_new_incident=True), 'not_applicable'), (dict(known_new_incident=None), 'cannot_determine')])
def test_later_vper_prerequisites(kw, status):
    r = later_vper(S(2025, 'high', **{'first_vper_done': True, **kw}))
    assert r['status'] == status and r['value'] is None


def test_supervised_case_has_no_stated_interval():
    r = later_vper(S(2025, 'low', case_status='supervised', first_vper_done=True))
    assert r['status'] == 'not_stated' and r['value'] is None


def test_never_a_deadline_when_a_prerequisite_is_unknown():
    """Exhaustive: any None among the prerequisites -> no numeric deadline is produced."""
    for y, lvl in [(2019, l) for l in LEVELS[2019]] + [(2025, l) for l in LEVELS[2025]]:
        for jm, st, done, inc, sr in itertools.product((False, True, None), ('active', None), (False, True, None), (False, None), (False, None)):
            s = S(y, lvl, judicial_measures=jm, case_status=st, first_vper_done=done, known_new_incident=inc, special_relevance=sr)
            for fn, key in ((first_vper, 'max_days'), (later_vper, 'value')):
                r = fn(s)
                if r['status'] == 'cannot_determine':
                    assert r[key] is None
            if None in (st, inc) and done is not True:
                assert first_vper(s)['max_days'] is None


# ------------------------------------------------------------------------------------------- instruments
def test_incident_instrument_changes():
    assert assessment_instrument(S(2019, 'low'), 'new_complaint_or_breach')['instrument'] == 'VPER-C'
    assert assessment_instrument(S(2025, 'low'), 'new_complaint_or_breach')['instrument'] == 'VPR'
    assert assessment_instrument(S(2025, 'low'), 'cometa_breach_verified')['instrument'] == 'VPR'


def test_judicial_request():
    assert assessment_instrument(S(2025, 'low'), 'judicial_request')['instrument'] == 'VPER'
    assert assessment_instrument(S(2025, 'low'), 'judicial_request_possible_reoffence')['instrument'] == 'VPR'
    assert assessment_instrument(S(2019, 'low'), 'judicial_request_possible_reoffence')['status'] == 'not_stated'


def test_2019_reactivation_six_month_rule():
    assert assessment_instrument(S(2019, 'low', months_since_last_assessment=7), 'reactivation_new_complaint')['instrument'] == 'VPR'
    assert assessment_instrument(S(2019, 'low', months_since_last_assessment=6), 'reactivation_new_complaint')['instrument'] == 'VPR'
    assert assessment_instrument(S(2019, 'low', months_since_last_assessment=2), 'reactivation_new_complaint')['instrument'] == 'VPER-C'
    assert assessment_instrument(S(2019, 'low'), 'reactivation_new_complaint')['status'] == 'cannot_determine'


def test_unknown_event_not_invented():
    assert assessment_instrument(S(2019, 'low'), 'cometa_breach_verified')['status'] == 'not_stated'


# ------------------------------------------------------------------------------------------- notification
def test_vper_court_notification():
    assert vper_court_notification(S(2019, 'medium'), 'medium', 'low')['individual_oficio'] is True
    assert vper_court_notification(S(2025, 'medium'), 'medium', 'low')['individual_oficio'] is False
    assert vper_court_notification(S(2025, 'medium'), 'medium', 'high')['individual_oficio'] is True
    assert vper_court_notification(S(2019, 'medium'), 'medium', 'medium')['individual_oficio'] is False
    assert vper_court_notification(S(2025, 'low'), 'low', 'high', instrument='incident')['in_new_police_file'] is True


# ------------------------------------------------------------------------------------------- case status
def test_case_status_rules():
    assert case_status_rule(S(2019, 'low'))['rule'] == 'active_as_general_rule'
    assert case_status_rule(S(2019, 'no_appreciable'))['rule'] == 'inactivation_possible'
    assert case_status_rule(S(2019, 'no_appreciable', judicial_measures=True))['rule'] == 'active'
    assert case_status_rule(S(2025, 'low'))['rule'] == 'inactivation_or_supervision_possible'
    assert case_status_rule(S(2025, 'low', judicial_measures=None))['status'] == 'cannot_determine'
    assert case_status_rule(S(2025, 'medium', judicial_measures=None))['rule'] == 'active_as_general_rule'


# ------------------------------------------------------------------------------------------- ordinary inactivation
ALL_OK_2019_NA = dict(judicial_measures=False, evaluator_judgement_supports_inactivation=True)
ALL_OK_2019_LOW = dict(ALL_OK_2019_NA, victim_contacted=True, reassessed_after_first_judicial_action=True, reassessment_raised_level=False)
ALL_OK_2025 = dict(judicial_measures=False, evaluator_judgement_supports_inactivation=True, victim_contacted=True,
                   reassessed_after_first_judicial_action=True)
NO_SUP = dict(special_relevance_or_minors_last_12m=False, medium_plus_last_3m=False, two_plus_complaints_first_6m=False)


def test_2019_ordinary_inactivation():
    r = ordinary_inactivation(S(2019, 'no_appreciable', **ALL_OK_2019_NA))
    assert (r['status'], r['permission']) == ('eligible', 'general_permission')
    assert ordinary_inactivation(S(2019, 'low', **ALL_OK_2019_LOW))['permission'] == 'exceptional_permission'
    assert ordinary_inactivation(S(2019, 'low', **{**ALL_OK_2019_LOW, 'reassessment_raised_level': True}))['status'] == 'insufficient_conditions'
    assert ordinary_inactivation(S(2019, 'no_appreciable', judicial_measures=False))['status'] == 'cannot_determine'
    assert ordinary_inactivation(S(2019, 'no_appreciable', **{**ALL_OK_2019_NA, 'judicial_measures': True}))['status'] == 'not_eligible'
    assert ordinary_inactivation(S(2019, 'medium', **ALL_OK_2019_NA))['status'] == 'not_eligible'


def test_2025_ordinary_inactivation_and_supervision():
    assert ordinary_inactivation(S(2025, 'low', **ALL_OK_2025, **NO_SUP))['status'] == 'eligible'
    assert ordinary_inactivation(S(2025, 'low', **ALL_OK_2025, **{**NO_SUP, 'medium_plus_last_3m': True}))['status'] == 'routes_to_supervision'
    assert ordinary_inactivation(S(2025, 'low', **ALL_OK_2025))['status'] == 'cannot_determine'           # supervision criteria unknown
    assert ordinary_inactivation(S(2025, 'low', **{**ALL_OK_2025, 'victim_contacted': None}, **NO_SUP))['status'] == 'cannot_determine'
    assert ordinary_inactivation(S(2025, 'low', **{**ALL_OK_2025, 'evaluator_judgement_supports_inactivation': False}, **NO_SUP))['status'] == 'insufficient_conditions'
    assert ordinary_inactivation(S(2025, 'medium', **ALL_OK_2025, **NO_SUP))['status'] == 'not_eligible'
    assert ordinary_inactivation(S(2025, 'low', **{**ALL_OK_2025, 'judicial_measures': True}, **NO_SUP))['status'] == 'not_eligible'


def test_supervision_criteria():
    assert supervision(S(2019, 'low'))['status'] == 'not_stated'
    assert supervision(S(2025, 'low', two_plus_complaints_first_6m=True))['criteria_met'] == ['two_plus_complaints_first_6m']
    assert supervision(S(2025, 'low', **NO_SUP))['status'] == 'not_applicable'
    assert supervision(S(2025, 'low', medium_plus_last_3m=False))['status'] == 'cannot_determine'
    assert '3 months' in supervision(S(2025, 'low', medium_plus_last_3m=True))['procedure']['minimum']


# ------------------------------------------------------------------------------------------- exceptional inactivation
def test_non_location_thresholds():
    assert exceptional_inactivation(S(2019, 'high'), 'victim_not_located', 1)['status'] == 'eligible'
    assert exceptional_inactivation(S(2019, 'high'), 'victim_not_located', 0.5)['status'] == 'not_eligible'
    assert exceptional_inactivation(S(2025, 'high'), 'victim_not_located', 2)['status'] == 'not_eligible'
    r = exceptional_inactivation(S(2025, 'high'), 'victim_not_located', 3)
    assert r['status'] == 'eligible' and 'notify the judicial police unit' in r['duties']
    assert exceptional_inactivation(S(2025, 'high'), 'victim_not_located')['status'] == 'cannot_determine'


def test_renunciation_scope():
    assert exceptional_inactivation(S(2019, 'extreme', judicial_measures=False), 'victim_renounces')['status'] == 'eligible'
    assert exceptional_inactivation(S(2025, 'high', judicial_measures=False), 'victim_renounces')['status'] == 'not_eligible'
    assert exceptional_inactivation(S(2025, 'medium', judicial_measures=False), 'victim_renounces')['status'] == 'eligible'
    assert exceptional_inactivation(S(2025, 'low', judicial_measures=True), 'victim_renounces')['status'] == 'not_eligible'
    assert exceptional_inactivation(S(2025, 'low', judicial_measures=None), 'victim_renounces')['status'] == 'cannot_determine'


def test_modal_shift_and_judgement_grounds():
    assert 'podrá' in exceptional_inactivation(S(2019, 'low'), 'death')['verb']
    assert 'se procederá' in exceptional_inactivation(S(2025, 'low'), 'death')['verb']
    assert exceptional_inactivation(S(2025, 'low'), 'abroad')['status'] == 'requires_judgement'
    assert exceptional_inactivation(S(2025, 'low'), 'analogous')['status'] == 'requires_judgement'
    assert exceptional_inactivation(S(2025, 'extreme'), 'homicide')['status'] == 'not_eligible'
    with pytest.raises(ValueError):
        exceptional_inactivation(S(2025, 'low'), 'moved_house')


# ------------------------------------------------------------------------------------------- reactivation
def test_reactivation():
    assert reactivation(S(2019, 'low'), 'other_change')['instrument'] == 'VPER-S'
    assert reactivation(S(2025, 'low'), 'new_complaint_or_breach')['instrument'] == 'VPR'
    assert reactivation(S(2025, 'low', judicial_measures=False), 'other_change', 'low')['reactivate'] is False
    assert reactivation(S(2025, 'low', judicial_measures=False), 'other_change', 'medium')['reactivate'] is True
    assert reactivation(S(2025, 'low', judicial_measures=True), 'other_change', 'low')['reactivate'] is True
    assert reactivation(S(2025, 'low', judicial_measures=False), 'other_change')['status'] == 'cannot_determine'


# ------------------------------------------------------------------------------------------- protection floor
def test_protection_floor_cumulative_and_conditional():
    for y in (2019, 2025):
        counts = [protection_floor(y, l, True, True, True)['n_items'] for l in LEVELS[y]]
        assert counts == sorted(counts)
    assert protection_floor(2025, 'low', True)['n_items'] - protection_floor(2025, 'low', False)['n_items'] == 3
    assert 'A2-2025-26' in protection_floor(2025, 'medium', special_relevance=True)['measure_ids']
    assert 'A2-2025-26' not in protection_floor(2025, 'medium', special_relevance=False)['measure_ids']
    assert 'A1-2019-18' in protection_floor(2019, 'medium')['measure_ids']                  # device request for all medio
    assert protection_floor(2025, 'low', minors_in_care=True)['n_items'] - protection_floor(2025, 'low')['n_items'] == 6
    assert set(protection_floor(2025, 'low', judicial_measures=None)['unknown_condition_items']) == {'A2-2025-15', 'A2-2025-16', 'A2-2025-17'}


# ------------------------------------------------------------------------------------------- pathways
def test_abstract_pathways():
    rows = enumerate_abstract_pathways()
    assert len(rows) == 50 and sum(r['year'] == 2019 for r in rows) == 30
    assert len({r['pathway_id'] for r in rows}) == 50
    assert all(r['clause_ids'] for r in rows)
    na = [r for r in rows if r['year'] == 2025 and r['officer_category'] == 'low' and not r['judicial_measures']][0]
    assert na['first_vper_status'] == 'not_stated' and na['later_vper_value'] == 90


def test_trace_contains_sources():
    t = trace(S(2025, 'low'))
    assert t['source_id'] == 'SES-1-2025' and t['source_url'].startswith('https://')
