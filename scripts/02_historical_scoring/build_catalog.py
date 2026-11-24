"""Build the VPR4.0 Annex 1 catalogue (vpr4_0_annex1_indicators.csv) from the verified transcription.

Source: Juan José López Ossorio (2016), doctoral thesis, Universidad Autónoma de Madrid.
  * Annex 1, pp. 274-275: labels and weights ("Odds ratio" column), transcribed in tools/annex1_transcription.py
    and checked against the PDF text layer by tests/test_source_transcription.py.
  * Table 1, p. 193: the 13 critical indicators.
  * Annex 2, pp. 276-277: the VioGén screen for VPR4.0 (factors F01-F12, Sí/No/No se sabe, checkboxes, radios).
  * Annex 5, pp. 291-307: filling instructions (conditional sub-questions, "se pueden marcar varias opciones").

Educational historical reconstruction only. Never for operational use, never VioGén 2.
"""
import csv
from pathlib import Path
from tools.annex1_transcription import ROWS

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'data' / '02_historical_scoring' / 'vpr4_0_annex1_indicators.csv'
SOURCE = 'López Ossorio (2016), doctoral thesis, UAM, Annex 1'
SOURCE_URL = 'https://repositorio.uam.es/server/api/core/bitstreams/09c11ef0-a544-439a-a623-4e492db41610/content'

FACTORS = {  # Annex 5 (pp. 292-307) and Annex 2 (pp. 276-277)
    'F01': (1, '¿Ha existido algún tipo de violencia por parte del agresor?'),
    'F02': (1, '¿Ha empleado el agresor armas u objetos contra la víctima?'),
    'F03': (1, '¿La víctima recibe o ha recibido amenazas o planes dirigidos a causar daño físico/psicológico?'),
    'F04': (1, '¿Ha existido una escalada en la gravedad y/o la frecuencia de las agresiones o las amenazas de violencia en los últimos seis meses?'),
    'F05': (1, 'Celos exagerados, control y acoso, en los últimos seis meses'),
    'F06': (2, '¿Ha mostrado el agresor alguno de estos comportamientos en el último año?'),
    'F07': (2, 'En los últimos seis meses, ¿existen indicios de problemas en la vida del agresor?'),
    'F08': (2, '¿El agresor tiene antecedentes penales y/o policiales?'),
    'F09': (2, '¿Se da alguna de las siguientes circunstancias en el agresor?'),
    'F10': (3, '¿Se da alguna de las siguientes circunstancias de vulnerabilidad en la víctima?'),
    'F11': (3, 'Circunstancias agravantes'),
    'F12': (4, 'La mujer piensa que el agresor es capaz de agredirla con mucha violencia o incluso matarla'),
}
CATEGORIES = {1: 'Historia de violencia. Valoración del episodio denunciado',
              2: 'Factores e indicadores relacionados con el agresor',
              3: 'Vulnerabilidad de la víctima y calidad de la relación',
              4: 'Percepción de la víctima sobre su situación'}

# row -> (code, factor, english label, parent code, response type, critical number in Table 1 p.193, evidence note)
G, IND, SEV, CHK, SUB = 'gate_question', 'indicator', 'severity_option', 'subtype_checkbox', 'sub_question'
SPEC = {
 1: ('I1_psychological', 'F01', 'Psychological violence (humiliation, insults)', '', IND, None, 'Annex 2: I01 Sí/No/No se sabe'),
 2: ('I1_psychological_severe', 'F01', 'Severe or very severe psychological violence', 'I1_psychological', SEV, None,
     'Annex 2: severity radio Leves/Graves/Muy graves under I01; Annex 5 p.292 defines the levels'),
 3: ('I2_physical', 'F01', 'Physical violence', '', IND, None, 'Annex 2: I02 Sí/No/No se sabe'),
 4: ('I2_physical_injuries', 'F01', 'Physical violence with or without injuries', 'I2_physical', SUB, None,
     'Nested under I2 in Annex 1; no matching control is visible on the Annex 2 screen (mapping unresolved; weight 0)'),
 5: ('I2_physical_severe', 'F01', 'Severe or very severe physical violence', 'I2_physical', SEV, 1,
     'Annex 2: severity radio Leve/Grave/Muy grave under I02; Annex 5 p.293'),
 6: ('I3_sexual', 'F01', 'Sexual violence', '', IND, None, 'Annex 2: I03 Sí/No/No se sabe'),
 7: ('I3_sexual_injuries', 'F01', 'Sexual violence with injuries', 'I3_sexual', SUB, None,
     'Nested under I3 in Annex 1; no matching control visible on the Annex 2 screen (mapping unresolved; weight 0)'),
 8: ('I3_sexual_severe', 'F01', 'Severe or very severe sexual violence', 'I3_sexual', SEV, 2,
     'Annex 2: severity radio Leve/Grave/Muy grave under I03; Annex 5 pp.293-294'),
 9: ('I4_defensive_reaction', 'F01', 'Victim reacted defensively to the aggression', '', IND, None, 'Annex 2: I04'),
 10: ('F02_weapons_used', 'F02', 'Aggressor used weapons or objects against the victim (factor 2 question)', '', G, None,
      'Annex 1 row without I-number above the I5 block; Annex 2: F02 Sí/No'),
 11: ('I5_knife', 'F02', 'Aggressor used a bladed weapon (knife)', 'F02_weapons_used', CHK, 3,
      'Annex 5 p.294: "en caso afirmativo ... arma blanca, arma de fuego y otros objetos. Se pueden marcar varias opciones"'),
 12: ('I5_firearm_use', 'F02', 'Aggressor used a firearm', 'F02_weapons_used', CHK, None, 'Annex 5 p.294 (as row 11)'),
 13: ('I5_other_object', 'F02', 'Aggressor used other objects', 'F02_weapons_used', CHK, None, 'Annex 5 p.294 (as row 11)'),
 14: ('I6_firearm_access', 'F02', 'Aggressor has access to firearms', '', IND, None,
      'Annex 5 p.295: assessed "independientemente de si empleó armas"; not conditional on F02'),
 15: ('F03_threats', 'F03', 'Victim receives or has received threats or plans to cause harm (factor 3 question)', '', G, None,
      'Annex 1 row without I-number above the I7 block; Annex 2: F03 Sí/No/No se sabe'),
 16: ('I7_severe_threat', 'F03', 'Serious threats aimed at causing harm', 'F03_threats', SEV, None,
      'Inferred to be the Graves/Muy graves options of the threat-severity radio (Annex 2; Annex 5 pp.295-296)'),
 17: ('I7_suicide_threat', 'F03', 'Aggressor threatens suicide', 'F03_threats', CHK, None,
      'Annex 5 p.295: "En caso de existir amenazas ... Se pueden marcar varias opciones"'),
 18: ('I7_economic_threat', 'F03', 'Economic threats by the aggressor', 'F03_threats', CHK, None, 'Annex 5 p.295'),
 19: ('I7_death_threat', 'F03', 'Death threats by the aggressor', 'F03_threats', CHK, 4, 'Annex 5 p.295'),
 20: ('I7_reputation_threat', 'F03', "Threats to the victim's social reputation", 'F03_threats', CHK, None, 'Annex 5 p.295'),
 21: ('I7_children_threat', 'F03', 'Threats to the integrity or custody of the children', 'F03_threats', CHK, None, 'Annex 5 p.295'),
 22: ('I8_escalation', 'F04', 'Escalation in severity and/or frequency in the last six months', '', IND, 5, 'Annex 5 p.296: factor 4 = indicator 8'),
 23: ('I9_jealousy', 'F05', 'Exaggerated jealousy or suspicion of infidelity (last 6 months)', '', IND, 6, 'Annex 2: I09 under F05'),
 24: ('I10_control_general', 'F05', 'Controlling behaviour (last 6 months)', '', IND, None, 'Annex 2: I10 under F05'),
 25: ('I10_control_physical', 'F05', 'Physical control (limits movement)', 'I10_control_general', CHK, None,
      'Annex 5 p.297: "En caso afirmativo ... permitiéndose señalar distintas opciones"'),
 26: ('I10_control_psychological', 'F05', 'Psychological and/or social control', 'I10_control_general', CHK, None, 'Annex 5 pp.297-298'),
 27: ('I10_control_work', 'F05', 'School or work control', 'I10_control_general', CHK, None, 'Annex 5 p.298'),
 28: ('I10_control_economic', 'F05', 'Economic control', 'I10_control_general', CHK, None, 'Annex 5 p.298'),
 29: ('I10_control_cyber', 'F05', 'Cyber control (social media, messages, calls)', 'I10_control_general', CHK, None, 'Annex 5 p.298'),
 30: ('I11_stalking', 'F05', 'Stalking or harassment (last 6 months)', '', IND, 7, 'Annex 2: I11 under F05'),
 31: ('I12_material_damage', 'F06', 'Property damage (last year)', '', IND, None, 'Annex 2: I12 under F06'),
 32: ('I13_disrespect_authority', 'F06', 'Disrespect for authority (last year)', '', IND, None, 'Annex 2: I13'),
 33: ('I14_attack_others_animals', 'F06', 'Physically attacks third parties and/or animals (last year)', '', IND, 8, 'Annex 2: I14'),
 34: ('I15_confrontation_others', 'F06', 'Physical or verbal confrontations with third parties (last year)', '', IND, None, 'Annex 2: I15'),
 35: ('I16_problems_general', 'F07', 'Signs of problems in the aggressor\'s life (last 6 months)', '', IND, None,
      'Annex 5 p.301: factor 7 "corresponde con el Indicador 16"'),
 36: ('I16_work_economic_problems', 'F07', 'Work or economic problems (last 6 months)', 'I16_problems_general', CHK, None,
      'Annex 5 p.301: "en caso de existir ... se deberá concretar el tipo ... Se permite marcar varias opciones"'),
 37: ('I16_legal_problems', 'F07', 'Problems with the justice system (last 6 months)', 'I16_problems_general', CHK, None, 'Annex 5 p.301'),
 38: ('F08_criminal_record', 'F08', 'Aggressor has a criminal and/or police record (factor 8 question)', '', G, None,
      'Annex 1 row without I-number above I17-I19; Annex 2: F08 Sí/No'),
 39: ('I17_prior_breaches', 'F08', 'Previous breaches of precautionary or criminal measures', 'F08_criminal_record', IND, None,
      'Annex 5 p.301: "en caso afirmativo, se debe especificar si existen quebrantamientos previos ... (Indicador 17)"'),
 40: ('I18_prior_aggression', 'F08', 'Record of physical and/or sexual aggression against others', 'F08_criminal_record', IND, None,
      'Annex 5 p.301: "... antecedentes por agresiones físicas y/o sexuales a terceras personas (Indicador 18)"'),
 41: ('I19_prior_ipv_other_partners', 'F08', 'Record of gender violence against other partners', 'F08_criminal_record', IND, None,
      'Annex 5 p.301: "... antecedentes de violencia de género sobre otra/s víctima/s (Indicador 19)"'),
 42: ('I20_mental_disorder', 'F09', 'Aggressor has a diagnosed mental/psychiatric disorder', '', IND, 9,
      'p.192: weight fixed at 3 ("puntuación directa de 3")'),
 43: ('I21_suicide_ideation', 'F09', 'Aggressor shows suicidal ideas or attempts', '', IND, 10, 'Annex 2: I21'),
 44: ('I22_substance_abuse', 'F09', 'Aggressor has an addiction or substance abuse', '', IND, 11, 'Annex 2: I22'),
 45: ('I23_family_history', 'F09', 'Family history of gender or domestic violence (aggressor)', '', IND, None, 'Annex 2: I23'),
 46: ('I24_disability', 'F10', 'Victim has a disability', '', IND, None, 'Annex 2: I24'),
 47: ('I25_pregnancy', 'F10', 'Victim is pregnant', '', IND, None, 'Annex 2: I25'),
 48: ('I26_serious_illness', 'F10', 'Victim has a serious illness', '', IND, None, 'Annex 2: I26'),
 49: ('I27_foreign', 'F10', 'Victim is a foreign national', '', IND, None, 'Annex 2: I27'),
 50: ('I28_social_support', 'F10', 'Victim lacks family or social support', '', IND, None, 'Annex 2: I28'),
 51: ('I29_mental_disorder', 'F10', 'Victim has a diagnosed mental/psychiatric disorder', '', IND, None, 'Annex 2: I29'),
 52: ('I30_suicidal', 'F10', 'Victim shows suicidal ideas or attempts', '', IND, None, 'Annex 2: I30'),
 53: ('I31_substance_abuse', 'F10', 'Victim has an addiction or substance abuse', '', IND, None, 'Annex 2: I31'),
 54: ('I32_prior_ipv', 'F10', 'Victim has a history of gender or domestic violence', '', IND, None,
      'Annex 5 p.304: two options, "Se permite marcar las dos opciones"; exact row-to-checkbox mapping unresolved'),
 55: ('I32_family_ipv', 'F10', 'Victim has a family history of gender or domestic violence', '', CHK, None, 'Annex 5 p.304 (as row 54)'),
 56: ('I33_economic_dependence', 'F10', 'Victim depends economically on the aggressor', '', IND, None, 'Annex 2: I33'),
 57: ('I34_dependents', 'F10', 'Victim cares for minors or dependent relatives', '', IND, None, 'Annex 2: I34'),
 58: ('I35_prior_reports', 'F11', 'Victim has reported other aggressors in the past', '', IND, None, 'Annex 2: I35'),
 59: ('I35_withdrawn_reports', 'F11', 'Victim has withdrawn reports in the past', '', SUB, None,
      'Annex 5 p.305: also covers reports against the current aggressor; "Se pueden marcar ambos" (not conditional)'),
 60: ('I36_recent_separation', 'F11', 'Victim told the aggressor she intends to end the relationship (last 6 months)', '', IND, 12, 'Annex 2: I36'),
 61: ('I37_reciprocal', 'F11', 'Episodes of reciprocal violence recorded', '', IND, None,
      'Annex 5 p.306: never asked literally; the officer must infer it'),
 62: ('I38_family_fear', 'F11', 'Victim fears for the minors or relatives in her care', '', IND, None, 'Annex 2: I38'),
 63: ('I39_victim_fear_lethal', 'F12', 'Victim thinks the aggressor could seriously harm or even kill her', '', IND, 13, 'Annex 2: F12 / I39'),
}

def build():
    rows = []
    for (row, page, group, es, val) in ROWS:
        code, factor, en, parent, rtype, crit, ev = SPEC[row]
        cat = FACTORS[factor][0]
        rows.append(dict(row=row, page=page, code=code, indicator=group, factor=factor, factor_question_es=FACTORS[factor][1],
                         category=cat, category_es=CATEGORIES[cat], spanish_source_label=es, english_label=en,
                         weight=f'{float(val):.3f}', weight_as_printed=val, parent_code=parent, response_type=rtype,
                         critical_indicator='yes' if crit else 'no', critical_table1_number=crit or '',
                         structure_evidence=ev, source=f'{SOURCE}, p. {page}', source_url=SOURCE_URL))
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    return rows

if __name__ == '__main__':
    r = build()
    print(len(r), 'rows written to', OUT.name)
