"""Documentary rules engine for the 2019 and 2025 VioGén police protocols (version 2).

For research use only. It NEVER computes a risk level: the automatic level is an input, as in the texts.
It encodes what Instrucción 4/2019 and Instrucción 1/2025 say happens next, and returns "cannot_determine" whenever
a prerequisite the text depends on is unknown (None). It is not police guidance and says nothing about practice.

Every output carries the clause_ids it rests on (see src/module3_sources.py and data/protocol_clauses.csv).
Standard library only.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Optional

LEVELS = {2019: ('no_appreciable', 'low', 'medium', 'high', 'extreme'),
          2025: ('low', 'medium', 'high', 'extreme')}
LEVEL_ES = {'no_appreciable': 'No apreciado', 'low': 'Bajo', 'medium': 'Medio', 'high': 'Alto', 'extreme': 'Extremo'}
SOURCE = {2019: 'SES-4-2019', 2025: 'SES-1-2025'}
URLS = {2019: 'https://violenciagenero.igualdad.gob.es/wp-content/uploads/InstrucciOn_4-2019.pdf',
        2025: 'https://mundopolicial.net/wp-content/uploads/instruccion-1.2025-s.e.s.-viogen.pdf'}
CASE_STATUS = ('active', 'inactive', 'supervised')

# later VPER intervals (strict: "antes de")
PERIODIC = {'extreme': (72, 'hours'), 'high': (7, 'days'), 'medium': (30, 'days')}

APPLIES, NOT_APPLICABLE, UNKNOWN, NOT_STATED, JUDGEMENT = 'applies', 'not_applicable', 'cannot_determine', 'not_stated', 'requires_judgement'


@dataclass(frozen=True)
class Scenario:
    """A fictitious, documentary scenario. None means "unknown" and is never silently turned into False."""
    version: int
    algorithm_category: str                      # assigned by the system; given, never computed
    officer_category: Optional[str] = None       # final level after the officer's review (None = kept)
    judicial_measures: Optional[bool] = False    # judicial (criminal) measures / order of protection in force
    case_status: Optional[str] = 'active'        # 'active' | 'inactive' | 'supervised' | None
    first_vper_done: Optional[bool] = None       # has the first VPER after the VPR taken place?
    known_new_incident: Optional[bool] = False   # new complaint or breach of measures
    special_relevance: Optional[bool] = False    # system flag "Caso de Especial Relevancia"
    minors_in_care: Optional[bool] = False
    # ordinary-inactivation premises
    victim_contacted: Optional[bool] = None
    reassessed_after_first_judicial_action: Optional[bool] = None
    reassessment_raised_level: Optional[bool] = None             # 2019 2.6.iii: "sin que este se haya elevado"
    evaluator_judgement_supports_inactivation: Optional[bool] = None
    # 2025 supervision criteria (7.4.1)
    special_relevance_or_minors_last_12m: Optional[bool] = None
    medium_plus_last_3m: Optional[bool] = None
    two_plus_complaints_first_6m: Optional[bool] = None
    # reactivation (2019 5.8)
    months_since_last_assessment: Optional[float] = None


DocumentaryScenario = Scenario   # name used in version 1


def _idx(version: int, level: str) -> int:
    if version not in LEVELS:
        raise ValueError('Protocol must be 2019 or 2025')
    if level not in LEVELS[version]:
        raise ValueError(f'Invalid {version} level {level!r}; allowed {LEVELS[version]!r}')
    return LEVELS[version].index(level)


def permitted_officer_levels(version: int, assigned: str) -> tuple[str, ...]:
    """Both texts provide only upward modification (2019 1.6, 5.10; 2025 3.8, 6.2)."""
    return LEVELS[version][_idx(version, assigned):]


def validate(s: Scenario) -> str:
    _idx(s.version, s.algorithm_category)
    final = s.officer_category or s.algorithm_category
    if _idx(s.version, final) < _idx(s.version, s.algorithm_category):
        raise ValueError('Downward modification is not provided by either protocol (2019 1.6/5.10; 2025 3.8/6.2)')
    if s.case_status not in CASE_STATUS + (None,):
        raise ValueError(f'case_status must be one of {CASE_STATUS} or None')
    if s.version == 2019 and s.case_status == 'supervised':
        raise ValueError('The 2019 protocol has no supervised state (created by Instrucción 2/2024)')
    return final


def _out(status, clauses, **kw):
    return dict(status=status, clause_ids=clauses, **kw)


# ----------------------------------------------------------------------------------------------- instruments
def assessment_instrument(s: Scenario, event: str) -> dict:
    """Which form the text prescribes for an event."""
    v = s.version
    table = {
        2019: {'initial': ('VPR', 'C19-1.1'), 'new_complaint_or_breach': ('VPER-C', 'C19-5.2-C'),
               'periodic_no_incident': ('VPER-S', 'C19-POST'), 'new_information': ('VPER-S (may)', 'C19-5.2-S'),
               'judicial_request': ('VPER-S', 'C19-5.2-S'), 'reactivation_other_cause': ('VPER-S', 'C19-5.9')},
        2025: {'initial': ('VPR', 'C25-3.1'), 'new_complaint_or_breach': ('VPR', 'C25-4.2'),
               'periodic_no_incident': ('VPER', 'C25-6.1'), 'new_information': ('VPER (must)', 'C25-4.1'),
               'judicial_request': ('VPER', 'C25-4.1'), 'judicial_request_possible_reoffence': ('VPR', 'C25-4.1'),
               'reactivation_new_complaint': ('VPR', 'C25-7.3.1'), 'reactivation_other_cause': ('VPER (must give Medio+ unless measures)', 'C25-7.3.2'),
               'prison_release_special_relevance': ('VPR + personal interview', 'C25-7.3.2-PRIS'),
               'cometa_breach_verified': ('VPR', 'C25-8-COMETA')},
    }
    if v == 2019 and event == 'reactivation_new_complaint':
        m = s.months_since_last_assessment
        if m is None:
            return _out(UNKNOWN, 'C19-5.8', instrument=None, reason='2019 5.8 depends on the months since the last assessment')
        return _out(APPLIES, 'C19-5.8', instrument='VPR' if m >= 6 else 'VPER-C',
                    reason='6 months or more since last assessment: VPR; less: VPER-C')
    if v == 2019 and event == 'judicial_request_possible_reoffence':
        return _out(NOT_STATED, 'C19-5.2-S', instrument='VPER-S', reason='2019 does not distinguish requests linked to a possible reoffence')
    if event not in table[v]:
        return _out(NOT_STATED, '', instrument=None, reason=f'Event {event!r} not provided for in the {v} protocol')
    inst, cl = table[v][event]
    return _out(APPLIES, cl, instrument=inst)


# ----------------------------------------------------------------------------------------------- first VPER
def first_vper(s: Scenario) -> dict:
    """Timing of the FIRST VPER after the VPR (distinct from later periodic VPER)."""
    final = validate(s)
    if s.case_status != 'active':
        return _out(UNKNOWN if s.case_status is None else NOT_APPLICABLE, '', min_days=None, max_days=None,
                    reason='Modelled only for active cases')
    if s.known_new_incident is None:
        return _out(UNKNOWN, '', min_days=None, max_days=None, reason='Unknown whether a new incident occurred')
    if s.known_new_incident:
        return _out(NOT_APPLICABLE, 'C19-5.2-C' if s.version == 2019 else 'C25-4.2', min_days=None, max_days=None,
                    reason='A new complaint or breach routes to the incident form, not the routine first VPER')
    if s.first_vper_done:
        return _out(NOT_APPLICABLE, '', min_days=None, max_days=None, reason='First VPER already done; see later_vper')
    if s.special_relevance is None:
        return _out(UNKNOWN, '', min_days=None, max_days=None, reason='Special-relevance flag unknown; it changes the rule')
    trigger = 'after the first judicial action resolving the protection request'
    if s.version == 2019:
        if s.special_relevance:
            return _out(APPLIES, 'C19-5.5', min_days=7, max_days=None, after=None,
                        reason='2019 5.5: specially relevant cases, first VPER only after at least 7 days; no maximum stated')
        if final != 'no_appreciable':
            return _out(APPLIES, 'C19-5.3', min_days=None, max_days=7, after=trigger, reason='2019 5.3: at most 7 days after the VPR')
        if s.judicial_measures is None:
            return _out(UNKNOWN, 'C19-5.4', min_days=None, max_days=None, reason='No apreciado: depends on judicial measures')
        if s.judicial_measures:
            return _out(APPLIES, 'C19-5.4', min_days=None, max_days=7, after=trigger, reason='2019 5.4: no apreciado with judicial measures')
        return _out(NOT_STATED, 'C19-5.3; C19-5.4', min_days=None, max_days=None, reason='No deadline stated for no apreciado without judicial measures')
    # 2025
    if s.special_relevance and final in ('medium', 'high'):
        return _out(APPLIES, 'C25-4.5; C25-8.A', min_days=7, max_days=None, after=None,
                    reason='2025 4.5: special relevance at Medio/Alto, first VPER only after at least 7 days; no maximum stated')
    if s.special_relevance and final == 'extreme':
        return _out(JUDGEMENT, 'C25-4.3; C25-4.5-EXT; C25-8.A', min_days=None, max_days=15, after=trigger,
                    reason='Extremo special relevance: may be reassessed earlier at the specialised officers\' judgement; 4.3 maximum of 15 days (see uncertainty U04)')
    if final in ('medium', 'high', 'extreme'):
        return _out(APPLIES, 'C25-4.3', min_days=None, max_days=15, after=trigger, reason='2025 4.3: at most 15 days after the VPR')
    if s.judicial_measures is None:
        return _out(UNKNOWN, 'C25-4.4', min_days=None, max_days=None, reason='Bajo: depends on whether judicial measures result')
    if s.judicial_measures:
        return _out(APPLIES, 'C25-4.4', min_days=None, max_days=15, after=trigger, reason='2025 4.4: Bajo with judicial measures')
    return _out(NOT_STATED, 'C25-4.3; C25-4.4', min_days=None, max_days=None,
                reason='No first-VPER deadline is stated for Bajo without judicial measures (uncertainty U05)')


# ----------------------------------------------------------------------------------------------- later VPER
def later_vper(s: Scenario) -> dict:
    """Interval of the periodic VPER AFTER the first VPER: active case, no known incident."""
    final = validate(s)
    cl = 'C19-POST' if s.version == 2019 else 'C25-6.1; C25-6.1-BAJO'
    if s.case_status is None:
        return _out(UNKNOWN, cl, value=None, unit=None, bound=None, reason='Case status unknown')
    if s.case_status == 'inactive':
        return _out(NOT_APPLICABLE, cl, value=None, unit=None, bound=None, reason='Periodic schedule applies only while active')
    if s.case_status == 'supervised':
        return _out(NOT_STATED, 'C25-6.1; C25-7.4.2-VPER', value=None, unit=None, bound=None,
                    reason='Supervised: a VPER on entry (and at 3 months for special relevance); no periodic interval stated (U06)')
    if s.first_vper_done is None:
        return _out(UNKNOWN, cl, value=None, unit=None, bound=None, reason='Unknown whether the first VPER has taken place')
    if not s.first_vper_done:
        return _out(NOT_APPLICABLE, cl, value=None, unit=None, bound=None, reason='Before the first VPER: see first_vper')
    if s.known_new_incident is None:
        return _out(UNKNOWN, cl, value=None, unit=None, bound=None, reason='Unknown whether a new incident occurred')
    if s.known_new_incident:
        return _out(NOT_APPLICABLE, cl, value=None, unit=None, bound=None, reason='A known incident leaves the routine schedule')
    if final in PERIODIC:
        v, u = PERIODIC[final]
        return _out(APPLIES, cl, value=v, unit=u, bound='strictly_before', reason='Routine later VPER')
    if s.version == 2019:
        return _out(APPLIES, cl, value=90 if final == 'no_appreciable' else 60, unit='days', bound='strictly_before', reason='2019 routine later VPER-S')
    if s.judicial_measures is None:
        return _out(UNKNOWN, cl, value=None, unit=None, bound=None, reason='2025 Bajo: 60 or 90 days depending on judicial measures')
    return _out(APPLIES, cl, value=60 if s.judicial_measures else 90, unit='days', bound='strictly_before',
                reason='2025 Bajo with measures <60 d, without <90 d')


# ----------------------------------------------------------------------------------------------- notification
def vper_court_notification(s: Scenario, prior_level: str, new_level: str, instrument: str = 'routine') -> dict:
    """Individual communication of a VPER result to court and prosecutor (narrow procedure; other duties exist)."""
    a, b = _idx(s.version, prior_level), _idx(s.version, new_level)
    if instrument == 'incident':
        cl = 'C19-5.12' if s.version == 2019 else 'C25-4.2'
        return _out(APPLIES, cl, individual_oficio=False, in_new_police_file=True, reason='Incident assessment goes into the new diligencias')
    if s.version == 2019:
        return _out(APPLIES, 'C19-5.11', individual_oficio=b != a, in_new_police_file=False, reason='2019: on any variation of risk')
    return _out(APPLIES, 'C25-6.3', individual_oficio=b > a, in_new_police_file=False, reason='2025: only on an upward variation')


# ----------------------------------------------------------------------------------------------- case status
def case_status_rule(s: Scenario) -> dict:
    final = validate(s)
    if s.version == 2019:
        if s.judicial_measures:
            return _out(APPLIES, 'C19-4.1', rule='active', reason='Judicial measures keep the case active')
        if final != 'no_appreciable':
            return _out(APPLIES, 'C19-2.5; C19-4.2', rule='active_as_general_rule',
                        reason='Bajo+ active as a general rule; bajo may be inactivated exceptionally (2.6)')
        if s.judicial_measures is None:
            return _out(UNKNOWN, 'C19-2.6', rule=None, reason='No apreciado: depends on judicial measures')
        return _out(APPLIES, 'C19-2.6; C19-4.2', rule='inactivation_possible', reason='No apreciado without measures may be inactivated')
    if s.judicial_measures or final in ('medium', 'high', 'extreme'):
        return _out(APPLIES, 'C25-7-ACT', rule='active_as_general_rule', reason='Judicial measures or Medio+')
    if s.judicial_measures is None:
        return _out(UNKNOWN, 'C25-7-ACT', rule=None, reason='Bajo: depends on judicial measures')
    return _out(APPLIES, 'C25-7.1; C25-7.4.1-ER', rule='inactivation_or_supervision_possible', reason='Bajo without measures')


# ----------------------------------------------------------------------------------------------- supervision
def supervision(s: Scenario) -> dict:
    if s.version == 2019:
        return _out(NOT_STATED, '', criteria_met=None, procedure=None,
                    reason='No supervised state in the 2019 text; created by Instrucción 2/2024 (grade B/C evidence)')
    crit = {'special_relevance_or_minors_last_12m': s.special_relevance_or_minors_last_12m,
            'medium_plus_last_3m': s.medium_plus_last_3m, 'two_plus_complaints_first_6m': s.two_plus_complaints_first_6m}
    cl = 'C25-7.4.1-ER; C25-7.4.1-MED; C25-7.4.1-DEN'
    procedure = dict(on_entry='VPER (C25-7.4.2-VPER)',
                     minimum='3 months; +3 at specialised officers\' judgement (C25-7.4.2-MIN)',
                     special_relevance='3 months; up to two +3-month extensions; interview at first VPER; VPER and contact with the accused at 3 months (C25-7.4.2-ER)',
                     new_complaint='case becomes Active (C25-7.4.2-NEW)', measures='those of the level obtained at each moment',
                     exit='one VPER at Bajo + interview with the victim, unless impossible (recorded) (C25-7.4.2-EXIT)')
    if any(v is True for v in crit.values()):
        return _out(APPLIES, cl, criteria_met=[k for k, v in crit.items() if v], procedure=procedure,
                    reason='At least one 7.4.1 criterion holds: inactivation is delayed into supervision')
    if any(v is None for v in crit.values()):
        return _out(UNKNOWN, cl, criteria_met=None, procedure=None, reason='One or more 7.4.1 criteria unknown')
    return _out(NOT_APPLICABLE, cl, criteria_met=[], procedure=None, reason='No 7.4.1 criterion holds')


# ----------------------------------------------------------------------------------------------- inactivation
def ordinary_inactivation(s: Scenario) -> dict:
    """Whether the ORDINARY route is open. Even when open it is a permission ("podrá"), never a duty."""
    final = validate(s)
    if s.judicial_measures:
        cl = 'C19-2.6' if s.version == 2019 else 'C25-7.1-JM'
        return _out('not_eligible', cl, reason='Judicial measures in force exclude the ordinary route')
    if s.version == 2019:
        if final in ('medium', 'high', 'extreme'):
            return _out('not_eligible', 'C19-2.5; C19-2.6', reason='Ordinary route covers no apreciado and (exceptionally) bajo only')
        prem = [('no judicial measures', None if s.judicial_measures is None else not s.judicial_measures),
                ('circumstances do not advise otherwise (evaluator)', s.evaluator_judgement_supports_inactivation)]
        if final == 'low':
            prem += [('victim contacted at least once', s.victim_contacted),
                     ('5.3 reassessment done', s.reassessed_after_first_judicial_action),
                     ('reassessment did not raise the level', None if s.reassessment_raised_level is None else not s.reassessment_raised_level)]
        cl = 'C19-2.6; C19-2.6.ii' + ('; C19-2.6.iii' if final == 'low' else '')
        return _judge_premises(prem, cl, 'exceptional_permission' if final == 'low' else 'general_permission')
    # 2025
    if final != 'low':
        return _out('not_eligible', 'C25-7.1', reason='Ordinary route covers Bajo only')
    prem = [('no criminal judicial measures in force', None if s.judicial_measures is None else not s.judicial_measures),
            ('circumstances reliably show no objective conditions for a repeat (evaluator)', s.evaluator_judgement_supports_inactivation),
            ('victim contacted at least once (preferably in person)', s.victim_contacted),
            ('reassessment after the first judicial action that granted no protection', s.reassessed_after_first_judicial_action)]
    res = _judge_premises(prem, 'C25-7.1; C25-7.1-JM; C25-7.1-JUDG; C25-7.1-CONT', 'permission')
    if res['status'] != 'eligible':
        return res
    sup = supervision(s)
    if sup['status'] == APPLIES:
        return _out('routes_to_supervision', res['clause_ids'] + '; C25-7.4.1-ER', premises=res['premises'],
                    reason='Premises met, but a 7.4.1 criterion holds: the case becomes Supervised first')
    if sup['status'] == UNKNOWN:
        return _out(UNKNOWN, res['clause_ids'], premises=res['premises'], reason='Premises met; supervision criteria unknown')
    return res


def _judge_premises(prem, clauses, kind):
    listing = [dict(premise=p, met=v) for p, v in prem]
    if any(v is False for _, v in prem):
        return _out('insufficient_conditions', clauses, premises=listing, reason='At least one premise is not met')
    if any(v is None for _, v in prem):
        return _out(UNKNOWN, clauses, premises=listing, reason='At least one premise is unknown')
    return _out('eligible', clauses, premises=listing, permission=kind,
                reason='All premises met: the unit MAY inactivate (not obliged); a traceable record is required in 2025')


GROUNDS = ('victim_not_located', 'death', 'abroad', 'custody', 'analogous', 'victim_renounces', 'homicide')


def exceptional_inactivation(s: Scenario, ground: str, months_not_located: Optional[float] = None) -> dict:
    final = validate(s)
    if ground not in GROUNDS:
        raise ValueError(f'ground must be one of {GROUNDS}')
    if s.version == 2019:
        verb = 'permitted ("podrá")'
        if ground == 'homicide':
            return _out(NOT_STATED, 'C19-2.7', verb=None, duties=[], reason='2019 states no homicide-specific inactivation rule')
        if ground == 'victim_not_located':
            if months_not_located is None:
                return _out(UNKNOWN, 'C19-2.7', verb=verb, duties=[], reason='Months without locating the victim unknown')
            ok = months_not_located >= 1
            return _out('eligible' if ok else 'not_eligible', 'C19-2.7; C19-2.7-REC', verb=verb,
                        duties=['record causes in VioGén'], reason='2019: at least ONE month')
        if ground == 'victim_renounces':
            if s.judicial_measures is None:
                return _out(UNKNOWN, 'C19-2.8', verb=verb, duties=[], reason='Judicial measures unknown')
            return _out('not_eligible' if s.judicial_measures else 'eligible', 'C19-2.8; C19-2.8-FISCAL', verb=verb,
                        duties=['report to the prosecutor'], reason='2019: any level, if no judicial measures')
        status = JUDGEMENT if ground == 'analogous' else 'eligible'
        return _out(status, 'C19-2.7; C19-2.7-REC', verb=verb, duties=['record causes in VioGén'], reason=f'2019 2.7: {ground}')
    # 2025
    verb = 'mandatory ("se procederá")'
    rec = ['record causes and actions in VioGén-2', 'communicate to court and prosecutor']
    if ground == 'homicide':
        return _out('not_eligible', 'C25-PREL-HOM', verb='prohibited', duties=['Central Administration records the case'],
                    reason='2025: never inactivated after a homicide')
    if ground == 'victim_not_located':
        if months_not_located is None:
            return _out(UNKNOWN, 'C25-7.2.1-LOC', verb=verb, duties=[], reason='Months since last contact unknown')
        ok = months_not_located >= 3
        return _out('eligible' if ok else 'not_eligible', 'C25-7.2.1-LOC; C25-7.2.1-PJ; C25-7.2.1-REC', verb=verb,
                    duties=rec + ['notify the judicial police unit', 'oficio on the impossibility of protection'] if ok else [],
                    reason='2025: at least THREE months since last contact (2/2024: six, grade C)')
    if ground == 'victim_renounces':
        if final not in ('low', 'medium'):
            return _out('not_eligible', 'C25-7.2.2', verb=verb, duties=[], reason='2025: renunciation only at Bajo or Medio')
        if s.judicial_measures is None:
            return _out(UNKNOWN, 'C25-7.2.2', verb=verb, duties=[], reason='Judicial measures unknown')
        if s.judicial_measures:
            return _out('not_eligible', 'C25-7.2.2', verb=verb, duties=[], reason='Not with judicial measures in force')
        return _out('eligible', 'C25-7.2.2; C25-7.2.2-CAUSE', verb=verb,
                    duties=['look into the reasons for renunciation', 'oficio to court and prosecutor', 'record causes and efforts'],
                    reason='2025 7.2.2')
    if ground == 'abroad':
        return _out(JUDGEMENT, 'C25-7.2.1-ABR; C25-7.2.1-REC', verb=verb, duties=rec,
                    reason='Inactivation unless the protecting officer considers the departure should not lead to it')
    status = JUDGEMENT if ground == 'analogous' else 'eligible'
    return _out(status, 'C25-7.2.1; C25-7.2.1-REC', verb=verb, duties=rec, reason=f'2025 7.2.1: {ground}')


def reactivation(s: Scenario, cause: str, vper_level: Optional[str] = None) -> dict:
    """cause: 'new_complaint_or_breach' | 'other_change' | 'prison_release_special_relevance' (2025)."""
    if s.version == 2019:
        if cause == 'new_complaint_or_breach':
            inst = assessment_instrument(s, 'reactivation_new_complaint')
            return _out(inst['status'], 'C19-5.8', reactivate=True if inst['status'] == APPLIES else None, instrument=inst['instrument'], reason=inst['reason'])
        if cause == 'other_change':
            return _out(APPLIES, 'C19-5.9; C19-REACT', reactivate=True, instrument='VPER-S', reason='Activation by VPER-S whatever the result')
        return _out(NOT_STATED, '', reactivate=None, instrument=None, reason=f'{cause!r} not in the 2019 text')
    if cause == 'new_complaint_or_breach':
        return _out(APPLIES, 'C25-7.3.1', reactivate=True, instrument='VPR', reason='New VPR; inform court and prosecutor')
    if cause == 'prison_release_special_relevance':
        return _out(APPLIES, 'C25-7.3.2-PRIS', reactivate=True, instrument='VPR + personal interview', reason='Even without judicial measures')
    if cause != 'other_change':
        raise ValueError('unknown cause')
    if s.judicial_measures:
        return _out(APPLIES, 'C25-7.3.2', reactivate=True, instrument='VPER', reason='Judicial measures in force: reactivate whatever the level')
    if s.judicial_measures is None or vper_level is None:
        return _out(UNKNOWN, 'C25-7.3.2', reactivate=None, instrument='VPER', reason='Needs the VPER result and judicial-measure status')
    ok = _idx(2025, vper_level) >= _idx(2025, 'medium')
    return _out(APPLIES, 'C25-7.3.2', reactivate=ok, instrument='VPER', reason='Reactivate only if the VPER gives Medio or higher')


# ----------------------------------------------------------------------------------------------- protection floor
def protection_floor(version: int, level: str, judicial_measures: Optional[bool] = False,
                     special_relevance: Optional[bool] = False, minors_in_care: Optional[bool] = False) -> dict:
    """Annex measures as written for a level (cumulative). A written floor, not a statement about delivery."""
    from annex_measures import LEVEL_ORDER, MEASURES
    _idx(version, level)
    order = LEVEL_ORDER[version]
    upto = order[:order.index(level) + 1]
    items, conditional_unknown = [], []
    for m in MEASURES:
        if m['year'] != version:
            continue
        lvl, blk = m['level'], m['block']
        if lvl == 'minors':
            if minors_in_care is None:
                conditional_unknown.append(m['measure_id'])
            elif minors_in_care:
                items.append(m)
            continue
        if lvl not in upto:
            continue
        if blk == 'with_judicial_measures':
            if judicial_measures is None:
                conditional_unknown.append(m['measure_id'])
                continue
            if not judicial_measures:
                continue
        if blk == 'special_relevance':
            if special_relevance is None:
                conditional_unknown.append(m['measure_id'])
                continue
            if not special_relevance:
                continue
        items.append(m)
    by_mod = {}
    for m in items:
        by_mod[m['modality']] = by_mod.get(m['modality'], 0) + 1
    return dict(version=version, level=level, n_items=len(items), measure_ids=[m['measure_id'] for m in items],
                by_modality=by_mod, unknown_condition_items=conditional_unknown,
                clause_ids='C19-A1-CUM; C19-A1-EXTRA' if version == 2019 else 'C25-A2-CUM; C25-A2-EXTRA; C25-A2-REC',
                caveat='Written floor plus discretionary additions; delivery and recording are not observed')


# ----------------------------------------------------------------------------------------------- full trace
def trace(s: Scenario) -> dict:
    final = validate(s)
    return dict(protocol=s.version, source_id=SOURCE[s.version], source_url=URLS[s.version],
                assigned_level=s.algorithm_category, final_level=final,
                override='raised' if final != s.algorithm_category else 'retained',
                permitted_final_levels=list(permitted_officer_levels(s.version, s.algorithm_category)),
                incident_instrument=assessment_instrument(s, 'new_complaint_or_breach'),
                first_vper=first_vper(s), later_vper=later_vper(s), case_status_rule=case_status_rule(s),
                ordinary_inactivation=ordinary_inactivation(s), supervision=supervision(s),
                protection_floor=protection_floor(s.version, final, s.judicial_measures, s.special_relevance, s.minors_in_care),
                scenario=asdict(s),
                model_status='documentary abstraction of two protocol texts; not an operational prediction, not police guidance')


def enumerate_abstract_pathways() -> list[dict]:
    """Core grid: protocol x assigned level x permitted officer level x judicial measures (False/True) = 50 rows.
    All other inputs at their documentary defaults (active case, first VPER not yet done for first_vper and done for
    later_vper, no incident, no special relevance, inactivation premises unknown). NOT case histories, NOT a population."""
    rows = []
    for year, levels in LEVELS.items():
        for assigned in levels:
            for final in permitted_officer_levels(year, assigned):
                for jm in (False, True):
                    s0 = Scenario(year, assigned, final, judicial_measures=jm, first_vper_done=False)
                    s1 = Scenario(year, assigned, final, judicial_measures=jm, first_vper_done=True)
                    f, l, ina = first_vper(s0), later_vper(s1), ordinary_inactivation(s1)
                    rows.append(dict(
                        pathway_id=f'P{year}-{assigned[:3]}-{final[:3]}-{"JM" if jm else "noJM"}',
                        year=year, assigned_category=assigned, officer_category=final, judicial_measures=jm,
                        override='raised' if assigned != final else 'retained',
                        first_vper_status=f['status'], first_vper_max_days=f['max_days'], first_vper_min_days=f['min_days'],
                        later_vper_status=l['status'], later_vper_value=l['value'], later_vper_unit=l['unit'],
                        incident_instrument='VPER-C' if year == 2019 else 'VPR',
                        case_status_rule=case_status_rule(s1)['rule'],
                        ordinary_inactivation=ina['status'],
                        protection_floor_items=protection_floor(year, final, jm)['n_items'],
                        clause_ids='; '.join(x for x in (f['clause_ids'], l['clause_ids'], ina['clause_ids']) if x),
                        scope='abstract documentary pathway; not case-level evidence'))
    return rows


if __name__ == '__main__':
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    ap = argparse.ArgumentParser()
    ap.add_argument('--example', action='store_true')
    args = ap.parse_args()
    if args.example:
        for sc in [Scenario(2019, 'low', judicial_measures=False, first_vper_done=True),
                   Scenario(2025, 'low', judicial_measures=False, first_vper_done=True),
                   Scenario(2025, 'medium', 'high', judicial_measures=True, first_vper_done=False)]:
            t = trace(sc)
            print(json.dumps({k: t[k] for k in ('protocol', 'final_level', 'first_vper', 'later_vper', 'ordinary_inactivation')},
                             indent=1, ensure_ascii=False))
