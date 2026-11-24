"""Interface tests: drive the Streamlit app headlessly (streamlit.testing.v1.AppTest)."""
from pathlib import Path

import pytest

AppTest = pytest.importorskip('streamlit.testing.v1').AppTest
APP = str(Path(__file__).resolve().parents[1] / 'interactive_app.py')


def run_app():
    at = AppTest.from_file(APP, default_timeout=180).run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def metrics(at):
    return {m.label: m.value for m in at.metric}


def test_loads_with_blank_form():
    at = run_app()
    m = metrics(at)
    assert m['Additive score'] == '0.000'
    assert m['Automatic level (historical cut-offs)'] == 'No appreciable risk'
    assert len(at.radio) == 63
    assert (m['Firearm used (only)'], m['Knife used (only)']) == ('1.533', '5.533')


def test_preset_switch_resets_every_answer():
    at = run_app()
    at.selectbox(key='preset').set_value('Stalking + separation + victim fears lethal violence').run()
    assert metrics(at)['Additive score'] == '11.056'
    at.selectbox(key='preset').set_value('Knife used').run()
    assert metrics(at)['Additive score'] == '5.533'
    assert at.radio(key='ans_I39_victim_fear_lethal').value == 'No'
    assert at.radio(key='ans_F02_weapons_used').value == 'Sí'


def test_subitem_yes_sets_parent_and_parent_no_closes_subitems():
    at = run_app()
    assert at.radio(key='ans_I10_control_cyber').disabled                       # parent is No
    at.radio(key='ans_I10_control_general').set_value('No se sabe').run()
    assert not at.radio(key='ans_I10_control_cyber').disabled
    at.radio(key='ans_I10_control_cyber').set_value('Sí').run()
    assert at.radio(key='ans_I10_control_general').value == 'Sí'
    assert metrics(at)['Additive score'] == '3.762'                              # 2.184 + 1.578
    at.radio(key='ans_I10_control_general').set_value('No').run()
    assert at.radio(key='ans_I10_control_cyber').value == 'No'
    assert metrics(at)['Additive score'] == '0.000'


def test_unknown_answers_show_a_range_not_a_level():
    at = run_app()
    at.selectbox(key='preset').set_value('Two answers unknown ("No se sabe")').run()
    m = metrics(at)
    assert m['Additive score range'] == '8.226 – 14.596'
    assert m['Automatic level'] == 'Undetermined'
    assert m['Live score'] == '8.226 – 14.596'                                     # sidebar copy
    assert any('**Live level:** Undetermined' in x.value for x in at.sidebar.markdown)


def test_override_offers_only_equal_or_higher_levels():
    at = run_app()
    at.selectbox(key='preset').set_value('Stalking + separation + victim fears lethal violence').run()
    assert at.selectbox(key='override').options == ['Low', 'Medium', 'High', 'Extreme']
    at.selectbox(key='override').set_value('High').run()
    assert any('Raised by 2 level' in w.value for w in at.warning)


def test_no_appreciable_shows_discretionary_inactivation():
    at = run_app()
    text = ' '.join(m.value for m in at.markdown)
    assert 'MAY switch the case to inactive' in text
    at.checkbox(key='judicial').check().run()
    assert 'stays active because a judicial protection measure' in ' '.join(m.value for m in at.markdown)
