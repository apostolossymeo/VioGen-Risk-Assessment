"""Historical VPR4.0 laboratory: Streamlit interface. Research and teaching only.

Run:  streamlit run interactive_app.py
Not VioGén 2, not the operational software, never for a real person. Every scenario is fictitious.
"""
import pandas as pd
import streamlit as st

from vpr4_historical import (BY_CODE, CHILDREN, ITEMS, LEVEL_ES, LEVEL_ORDER, THRESHOLD_ROWS, apply_officer_override,
                             category_extremes, evaluate, make_case, procedural_consequences)
from build_catalog import FACTORS, CATEGORIES

SI, NO, NS = 'Sí', 'No', 'No se sabe'
TO_VALUE = {SI: True, NO: False, NS: None}
FROM_VALUE = {True: SI, False: NO, None: NS}

PRESETS = {
    'Blank form (every row No)': ([], []),
    'Firearm used': (['I5_firearm_use'], []),
    'Knife used': (['I5_knife'], []),
    'Stalking + separation': (['I11_stalking', 'I36_recent_separation'], []),
    'Stalking + separation + victim fears lethal violence': (['I11_stalking', 'I36_recent_separation', 'I39_victim_fear_lethal'], []),
    'Coding choice: insults recorded as psychological violence': (['I11_stalking', 'I36_recent_separation', 'I1_psychological'], []),
    'Two answers unknown ("No se sabe")': (['I11_stalking', 'I36_recent_separation'], ['I39_victim_fear_lethal', 'I9_jealousy']),
}

st.set_page_config(page_title='VPR4.0 historical lab', page_icon='🔎', layout='wide')


@st.cache_data
def extremes():
    return pd.DataFrame(category_extremes())


def load_preset(name: str) -> None:
    yes, unknown = PRESETS[name]
    case = make_case(*yes, unknown=unknown)
    for it in ITEMS:
        st.session_state['ans_' + it.code] = FROM_VALUE[case[it.code]]
    st.session_state['override'] = None


def on_change(code: str) -> None:
    """Keep the form consistent the way the VioGén screen does: a sub-item answered Sí makes its parent Sí;
    a parent answered No closes its sub-items (they are asked only "en caso afirmativo")."""
    value = st.session_state['ans_' + code]
    parent = BY_CODE[code].parent
    if parent and value == SI:
        st.session_state['ans_' + parent] = SI
    if code in CHILDREN and value == NO:
        for kid in CHILDREN[code]:
            st.session_state['ans_' + kid] = NO


if 'ans_' + ITEMS[0].code not in st.session_state:
    st.session_state['preset'] = list(PRESETS)[0]
    load_preset(st.session_state['preset'])

st.title('VPR4.0 (2016): how a police form turns answers into a risk level')
st.caption('Sciences Po · Data and Algorithms for Public Policy · Group D. Source: López Ossorio (2016), UAM doctoral '
           'thesis: Annex 1 pp. 274-275 (weights), pp. 192-194 (method, cut-offs), Annexes 2 and 5 (form), '
           'Annex 6 (Instrucción 7/2016).')
st.error('Historical reconstruction for teaching. This is NOT VioGén 2 (2025), not the police software, and must '
         'never be used to assess a real person or decide on protection. All scenarios are fictitious.')

with st.sidebar:
    st.header('Scenario')
    st.selectbox('Start from a fictitious scenario', list(PRESETS), key='preset',
                 on_change=lambda: load_preset(st.session_state['preset']))
    st.button('Reload this scenario', on_click=lambda: load_preset(st.session_state['preset']))
    st.markdown('**Answers**: *Sí* / *No* / *No se sabe*, as on the VioGén screen (Annex 2). Sub-items open only when '
                'their question is *Sí*. Unknown answers are never counted as *No*.')

answers = {it.code: TO_VALUE[st.session_state['ans_' + it.code]] for it in ITEMS}
result = evaluate(answers)
if result['complete']:
    live_score, live_level = f"{result['score']:.3f}", result['category']
else:
    live_score = f"{result['score_min']:.3f} – {result['score_max']:.3f}"
    live_level = result['category_at_min'] if result['category_robust_to_unknowns'] else 'Undetermined'
with st.sidebar:
    st.divider()
    st.subheader('Live result')          # stays in view while scrolling the 63 answers
    st.metric('Live score', live_score)
    st.markdown(f'**Live level:** {live_level}  \n*{LEVEL_ES.get(live_level, "indeterminado")}*')
st.markdown(f'**Current result:** score {live_score} → {live_level} (historical cut-offs). Details in section 2.')

left, right = st.columns([3, 2], gap='large')
with left:
    st.subheader('1 · The officer records the answers')
    st.caption('Input discretion: Annex 5 tells officers to pick the more severe level when in doubt, to raise '
               'severity when children were present, and to infer reciprocal violence (I37) rather than ask it.')
    for cat_no, cat_name in CATEGORIES.items():
        st.markdown(f'**Category {cat_no}. {cat_name}**')
        for f, (c, question) in FACTORS.items():
            if c != cat_no:
                continue
            rows = [it for it in ITEMS if it.factor == f]
            pts = sum(BY_CODE[r['code']].weight for r in result['contributions'] if BY_CODE[r['code']].factor == f)
            with st.expander(f'{f} · {question}  —  {pts:.3f} points', expanded=(f in ('F01', 'F02'))):
                for it in rows:
                    disabled = bool(it.parent) and st.session_state['ans_' + it.parent] == NO
                    label = (('↳ ' if it.parent else '') + f'{it.indicator or it.factor} · {it.english} '
                             f'**[{it.weight:.3f}]**' + (' · critical' if it.critical else ''))
                    st.radio(label, [SI, NO, NS], key='ans_' + it.code, horizontal=True, disabled=disabled,
                             on_change=on_change, args=(it.code,), help=it.spanish)

with right:
    st.subheader('2 · The designers\' weights add up')
    if result['complete']:
        st.metric('Additive score', f"{result['score']:.3f}")
        st.metric('Automatic level (historical cut-offs)', result['category'])
        st.caption(f"In the Spanish form: **{result['category_es']}**")
    else:
        st.metric('Additive score range', f"{result['score_min']:.3f} – {result['score_max']:.3f}")
        st.metric('Automatic level', 'Undetermined' if not result['category_robust_to_unknowns']
                  else f"{result['category_at_min']} (same at both ends)")
        st.caption(f"{result['unknown_count']} answers are 'No se sabe'. How the software scored them is not documented, "
                   'so the app shows every possible completion: from all unknowns No to all unknowns Sí.')
    st.progress(min(1.0, result['score_max'] / 77.019))
    st.dataframe(pd.DataFrame([dict(level=f'{lab} · {LEVEL_ES[lab]}', up_to=str(u) if u else '77.019')
                               for lab, u in THRESHOLD_ROWS]), hide_index=True, width='stretch')
    pos = [c for c in result['contributions'] if c['weight'] > 0]
    if pos:
        st.dataframe(pd.DataFrame(pos)[['indicator', 'label', 'weight', 'critical']], hide_index=True,
                     width='stretch')
    if result['zero_weight_positive']:
        st.info(f"{len(result['zero_weight_positive'])} rows answered Sí carry zero weight. The thesis kept such rows "
                'to collect information for about 18 months (p. 196); zero points is not evidence of safety.')
    if result['notes']['parent_implied']:
        st.caption('Parent questions set to Sí because a sub-item was Sí: ' + ', '.join(result['notes']['parent_implied']))

    st.subheader('3 · The procedure decides what follows')
    if result['complete'] or result['category_robust_to_unknowns']:
        auto = result['category_at_min']
        allowed = LEVEL_ORDER[LEVEL_ORDER.index(auto):]
        if st.session_state.get('override') not in allowed:
            st.session_state['override'] = auto
        final = st.selectbox('Final level after the officer\'s review (Instrucción 7/2016, rule 1.5: upwards only)',
                             allowed, key='override')
        ov = apply_officer_override(auto, final)
        if ov['raised_by_officer']:
            st.warning(f"Raised by {ov['steps_raised']} level(s). The rule offers no way to lower the automatic level.")
        judicial = st.checkbox('A judicial protection measure is in force', key='judicial')
        for line in procedural_consequences(final, judicial):
            st.write('• ' + line)
    else:
        st.caption('The level is undetermined, so the procedural consequences cannot be shown.')

st.divider()
st.subheader('Firearm versus knife: what the numbers do and do not say')
a, b, c = st.columns(3)
fire, knife = evaluate(make_case('I5_firearm_use')), evaluate(make_case('I5_knife'))
a.metric('Firearm used (only)', f"{fire['score']:.3f}")
b.metric('Knife used (only)', f"{knife['score']:.3f}")
c.metric('Difference', f"{knife['score'] - fire['score']:+.3f}")
st.write('Both start from the F02 question (1.533). The knife sub-item adds 4.000 because it is one of the 13 critical '
         'indicators chosen by expert consensus for a homicide-risk screening and doubled (pp. 191-193). Firearm use is not '
         'on that list; the thesis does not say why, and its sub-item adds 0. The empirical weights are odds ratios for a '
         '*new police report* against the same aggressor within four months (p. 191). In the study of the predecessor form '
         'VPR2015, firearm use appeared in 30 of 6,613 cases and its association was not significant (RR 1.408, 95% CI '
         '.479-4.134; Table 1, p. 163). This is a property of the sample and of the criterion, not a statement about how '
         'dangerous firearms are.')

with st.expander('Structural facts of the 2016 rule (exact, computed over every consistent form)'):
    st.dataframe(extremes(), hide_index=True, width='stretch')
    st.caption('Read across: the fewest and the most indicators (I1-I39) a form can have and still land in each level. '
               'The thesis notes a level can be reached "by many low-weight indicators or by fewer high-weight ones" (p. 192).')
