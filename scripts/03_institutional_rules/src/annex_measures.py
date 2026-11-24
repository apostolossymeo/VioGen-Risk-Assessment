"""Complete transcription of the police protection-measure annexes (version 2).

2019: Instrucción 4/2019, Anexo 1 "Medidas policiales de protección a adoptar para cada nivel de riesgo", pp. 15-18.
2025: Instrucción 1/2025, Anexo II "Medidas policiales de protección para cada nivel de riesgo", pp. 37-40.

Every bullet of both tables is transcribed (exhaustive=True). The Spanish text is the printed text (2019 transcribed
from the page images and checked against the OCR; 2025 from the PDF text layer and checked against the page images).
The ciberseguridad sub-bullets of 2025 Bajo item 10 are kept as one item.

`modality` classifies HOW the text obliges, using only words on the page:
  mandatory              bare instruction ("Facilitar...", "Entrevista personal...")
  conditional_fact       instruction that applies only if a stated fact holds ("Si el autor tuviera licencia...")
  conditional_judgement  applies when an officer appraises it relevant ("Si procede", "cuando se considere", "En atención a las circunstancias")
  resource_contingent    modality depends on available means ("en función de los medios disponibles")
  advice_to_victim       a recommendation the victim may or may not follow ("Recomendar", "Aconsejar", "Facilitar recomendaciones")
  request_other_authority  police ask another body, which decides ("Solicitar/Instar a Fiscalía", "Pedir información a Servicios Sociales")
  discretionary_option   police MAY do it ("puede ser difundida")
`decision_owner` names who finally decides whether the measure happens.
"""
from __future__ import annotations

LEVEL_ORDER = {2019: ['general', 'no_appreciable', 'low', 'medium', 'high', 'extreme'],
               2025: ['general', 'low', 'medium', 'high', 'extreme']}

M = []


def add(year, level, block, page, text_es, summary_en, modality, owner='police_unit', condition=''):
    n = sum(1 for m in M if m['year'] == year) + 1
    M.append(dict(measure_id=f'{"A1" if year == 2019 else "A2"}-{year}-{n:02d}', year=year, level=level, block=block,
                  pdf_page=str(page), text_es=text_es, summary_en=summary_en, modality=modality, decision_owner=owner,
                  condition=condition, exhaustive=True,
                  source_id='SES-4-2019' if year == 2019 else 'SES-1-2025',
                  annex='Anexo 1 (pp. 15-18)' if year == 2019 else 'Anexo II (pp. 37-40)'))


# ------------------------------------------------------------------------------------------------ 2019 Anexo 1
add(2019, 'no_appreciable', 'case_management', 15,
    'La Unidad policial especializada o la que gestione el Caso, se ocupará de que los datos contenidos en el mismo sean correctos y se encuentren debidamente actualizados, especialmente identificación correcta, completa y actualizada de AGRESOR y VÍCTIMA, así como contacto y domicilio de ambos y demás datos de interés.',
    'Keep case data correct and updated; avoid duplicate cases and IDs.', 'mandatory')
add(2019, 'no_appreciable', 'victim_information', 15,
    'Las mismas, de tipo orientativo, informativo y asistencial que para cualquier otro ciudadano. Especialmente información detallada de los recursos disponibles en su demarcación, tanto oficinas de atención a víctimas del delito (ámbito Justicia), como servicios sociales.',
    'Same guidance as any citizen, plus detailed information on local victim-support offices and social services.', 'mandatory')
add(2019, 'no_appreciable', 'victim_information', 15,
    'Facilitar recomendaciones en materia de autoprotección, pudiendo servir de orientación aquellas incluidas en el PSP y que se adapten a las circunstancias concretas de la víctima.',
    'Give self-protection advice (PSP items as guide).', 'advice_to_victim', owner='victim')
add(2019, 'low', 'victim_information', 16,
    'Facilitar a la víctima números de teléfono de contacto permanente (24 horas) con las FFCCS de asignación del caso.',
    '24-hour contact numbers of the assigned police unit.', 'mandatory')
add(2019, 'low', 'victim_information', 16, 'Facilitar información precisa sobre el servicio de tele asistencia móvil.',
    'Information on the mobile tele-assistance service.', 'mandatory')
add(2019, 'low', 'victim_information', 16,
    'Derivación de la víctima hacia oficinas de atención a víctimas del delito (ámbito Justicia) y servicios sociales que correspondan a su lugar de residencia',
    'Refer the victim to victim-support offices and social services.', 'mandatory')
add(2019, 'low', 'victim_operational', 16,
    'Contactos telefónicos y/o personales con la víctima. En el caso de contactos personales estos han de ser discretos, acordando con la víctima los mismos y la conveniencia de utilizar o no uniforme y/o vehículos con distintivos.',
    'Telephone and/or personal contacts; discreet; uniform/marked cars agreed with the victim.', 'mandatory')
add(2019, 'low', 'victim_operational', 16,
    'Indagar con la víctima para conocer momento de recepción y contenido de resoluciones judiciales que sobre el Caso se hayan podido emitir en el ámbito civil',
    'Ask the victim about civil court rulings (custody, support, housing) that may affect the aggressor\'s dangerousness.', 'mandatory')
add(2019, 'low', 'aggressor', 16,
    'Comunicación al agresor de que su Caso de violencia de género se encuentra sometido a control/protección policial y en su caso contenido y alcance de las Medidas Judiciales/Orden de Protección acordada.',
    'Tell the aggressor the case is under police control/protection (all bajo+ cases).', 'mandatory')
add(2019, 'low', 'aggressor', 16,
    'Si el agresor tuviera licencia de armas, requerirle la entrega voluntaria de las armas (si tuviera) y permiso a la Unidad policial actuante. Posteriormente solicitar la retirada judicial de ambas.',
    'If he holds a weapons licence: request voluntary surrender, then ask the court to withdraw both.', 'conditional_fact', condition='aggressor holds a weapons licence')
add(2019, 'low', 'aggressor', 16,
    'En atención a las circunstancias del Caso, acordar el acompañamiento del agresor al domicilio de la víctima, para retirar sus efectos, en el caso de que el Juez acuerde su salida del mismo.',
    'Escort the aggressor to collect belongings if the judge orders him out of the home.', 'conditional_judgement', condition='judge orders the aggressor out of the home')
add(2019, 'low', 'aggressor', 16,
    'Revisar puntualmente la información penitenciaria en el Sistema VioGén, al objeto de conocer, si las tuviera, las salidas penitenciarias del agresor',
    'Check prison information (leave, release) and confirm with the prison where in doubt.', 'mandatory')
add(2019, 'low', 'aggressor', 17,
    'El Sistema VioGén pone a disposición de los usuarios una Ficha dossier, en formato imprimible, que, a juicio de la Unidad policial gestora del Caso, siempre para garantizar un mejor control de agresor y seguridad de víctima, puede ser difundida a Unidades policiales de seguridad/patrullas de seguridad ciudadana.',
    'The case dossier MAY be circulated to patrol units at the managing unit\'s judgement.', 'discretionary_option')
add(2019, 'medium', 'victim_operational', 17, 'Entrevista personal con la víctima.', 'Personal interview with the victim.', 'mandatory')
add(2019, 'medium', 'victim_operational', 17,
    'Si procede, en atención a las circunstancias del Caso, efectuar traslado de la víctima para ingreso en centro de acogida.',
    'If appropriate, take the victim to a shelter.', 'conditional_judgement', owner='police_unit_and_victim')
add(2019, 'medium', 'victim_operational', 17,
    'Control ocasional de la víctima en domicilio, lugar de trabajo y centros escolares de los menores en horarios de entrada y salida.',
    'Occasional checks at home, work and the children\'s schools (an interview with support services is recommended first).', 'mandatory')
add(2019, 'medium', 'victim_operational', 17,
    'Acompañamiento a la víctima en actuaciones de carácter judicial, asistencial o administrativo, cuando se considere que puede existir algún tipo de riesgo para ella.',
    'Accompany the victim to court/assistance/administrative steps when a risk is considered to exist.', 'conditional_judgement')
add(2019, 'medium', 'aggressor', 17,
    'Instar a Fiscalía el seguimiento obligatorio del agresor a través de la asignación de un dispositivo telemático de control.',
    'Ask the prosecutor for compulsory electronic monitoring of the aggressor (ALL medio+ cases).', 'request_other_authority', owner='prosecutor_and_court')
add(2019, 'medium', 'aggressor', 17,
    'Comprobación periódica del cumplimiento por el agresor de las Medidas judiciales de protección impuestas, lo que incluirá control ocasional del mismo en domicilio, lugar de trabajo u otros.',
    'Periodic compliance checks, including occasional checks on the aggressor at home/work.', 'mandatory')
add(2019, 'medium', 'aggressor', 17,
    'Comunicación/entrevista con el agresor en permisos penitenciarios y/o excarcelaciones para informarle de que su Caso se encuentra sometido a control/protección policial',
    'Contact the aggressor on prison leave/release.', 'conditional_fact', condition='prison leave or release')
add(2019, 'high', 'victim_operational', 17,
    'En caso de no haberse podido localizar todavía al agresor, insistir a la víctima, para su más efectiva protección, en la posibilidad de traslado a centro de acogida, casa de un familiar o domicilio distinto.',
    'If the aggressor is not yet located, INSIST on relocation (shelter, relative, other address).', 'conditional_fact', owner='victim', condition='aggressor not yet located')
add(2019, 'high', 'victim_operational', 18,
    'Control frecuente y aleatorio en domicilio y lugar de trabajo de la víctima y, si procede en centros escolares de los hijos a la entrada y salida y contactos con personas de su entorno para mejor protección.',
    'FREQUENT and random checks at the victim\'s home and work (schools if appropriate).', 'mandatory')
add(2019, 'high', 'aggressor', 18,
    'Control aleatorio de los movimientos del agresor y contactos esporádicos con personas que este frecuente o de su entorno.',
    'Random control of the aggressor\'s movements; sporadic contacts with his circle.', 'mandatory')
add(2019, 'extreme', 'victim_operational', 18,
    'Protección permanente de la víctima hasta que el mismo agresor o sus circunstancias dejen de ser una amenaza inminente.',
    'Permanent protection until the threat is no longer imminent.', 'mandatory')
add(2019, 'extreme', 'victim_operational', 18,
    'Si procede, vigilancia en centros escolares de los hijos de la víctima a la hora de entrada y salida.',
    'If appropriate, surveillance at the children\'s schools.', 'conditional_judgement')
add(2019, 'extreme', 'aggressor', 18,
    'Control intensivo de los movimientos del agresor hasta que este deje de ser una amenaza inminente para la seguridad de la víctima.',
    'Intensive control of the aggressor\'s movements.', 'mandatory')

# ------------------------------------------------------------------------------------------------ 2025 Anexo II
add(2025, 'general', 'case_management', 37,
    'La Unidad policial que gestione el Caso se ocupará de que los datos contenidos en el mismo sean correctos y se encuentren debidamente actualizados, especialmente en lo relativo a información de contacto, domicilio y demás datos de interés.',
    'Keep case data correct and updated; avoid duplicates (row above all levels).', 'mandatory')
add(2025, 'general', 'victim_information', 37,
    'La víctima deberá ser informada de su nivel de riesgo, de sus factores más importantes, que el riesgo puede variar a lo largo del tiempo, así como de los peligros a los que se puede enfrentar.',
    'Inform the victim of her level, its main factors, that it can change, and the dangers.', 'mandatory')
add(2025, 'low', 'victim_information', 37, 'Las mismas, de tipo orientativo, informativo y asistencial que para cualquier otro ciudadano.',
    'Same guidance as any citizen.', 'mandatory')
add(2025, 'low', 'victim_information', 37, 'Facilitar a la víctima números de teléfono de contacto permanente (24 horas) con las FFCCS de asignación del Caso.',
    '24-hour contact numbers.', 'mandatory')
add(2025, 'low', 'victim_information', 37, 'Facilitar números de emergencia 112, 091, 062, 016, 092.', 'Emergency numbers.', 'mandatory')
add(2025, 'low', 'victim_information', 37, 'Facilitar información precisa sobre el servicio de teleasistencia móvil. Indicar la posible descarga de la aplicación AlertCops.',
    'Tele-assistance information; AlertCops app.', 'mandatory')
add(2025, 'low', 'victim_information', 37, 'Información y, en su caso, derivación de la víctima hacia oficinas de atención a víctimas del delito (ámbito Justicia) y servicios sociales.',
    'Information and, where appropriate, referral to victim-support offices and social services.', 'conditional_judgement')
add(2025, 'low', 'victim_information', 37, 'Facilitar recomendaciones en materia de autoprotección, pudiendo servir de orientación aquellas incluidas en el PSP y que se adapten a las circunstancias concretas de la víctima.',
    'Self-protection advice.', 'advice_to_victim', owner='victim')
add(2025, 'low', 'victim_operational', 37, 'Establecer contactos con la víctima que, en función de los medios disponibles, podrán ser personales o telefónicos.',
    'Contacts with the victim, in person or by phone DEPENDING ON AVAILABLE MEANS.', 'resource_contingent')
add(2025, 'low', 'victim_operational', 38, 'de las resoluciones judiciales que se hayan acordado, a fin de que tanto la víctima como el personal policial protector conozcan el alcance de estas.',
    'Use the contacts to exchange information on court rulings.', 'mandatory')
add(2025, 'low', 'victim_operational', 38, 'En el caso de contactos personales, estos han de ser discretos y se deben usar vehículos sin distintivos policiales y personal sin uniforme, salvo que las circunstancias lo imposibiliten.',
    'Personal contacts discreet: unmarked cars, plain clothes (default, not agreed with the victim).', 'mandatory')
add(2025, 'low', 'victim_information', 38, 'Realizar las siguientes recomendaciones a la víctima en relación con su ciberseguridad:',
    'Five cybersecurity recommendations (private profiles, followers, location, tagging, passwords).', 'advice_to_victim', owner='victim')
add(2025, 'low', 'aggressor', 38, 'Se informará al autor, que debe estar disponible o localizado cuando sea llamado a declarar a presencia policial y/o judicial.',
    'Tell the aggressor he must remain reachable for police/court.', 'mandatory')
add(2025, 'low', 'aggressor', 38, 'Si el autor tuviera licencia de armas, requerirle la entrega voluntaria de las armas y permiso a la Unidad policial actuante.',
    'If he holds a weapons licence: request voluntary surrender (no follow-up court request stated).', 'conditional_fact', condition='aggressor holds a weapons licence')
add(2025, 'low', 'with_judicial_measures', 38, 'Comunicar al autor de que su caso de violencia de género se encuentra sometido a control/protección policial y, en su caso, contenido y alcance de las medidas judiciales/orden de protección acordada.',
    'Tell the aggressor the case is under police control: ONLY where judicial measures exist.', 'conditional_fact', condition='judicial measures exist')
add(2025, 'low', 'with_judicial_measures', 38, 'Acordar el acompañamiento del autor al domicilio de la víctima, para retirar sus efectos, en el caso de que el juez acuerde su salida de este. Si es posible, se aconseja que el autor haga entrega de las llaves del referido domicilio.',
    'Escort the aggressor to collect belongings if ordered out; keys handed over if possible.', 'conditional_fact', condition='judicial measures exist; judge orders him out')
add(2025, 'low', 'with_judicial_measures', 38, 'Revisar la información penitenciaria en el Sistema VioGén-2, al objeto de conocer, si las tuviera, los movimientos del autor, informando a la víctima de los permisos/salidas penitenciarias.',
    'Check prison information and inform the victim of leave/release: ONLY where judicial measures exist.', 'conditional_fact', condition='judicial measures exist')
add(2025, 'low', 'case_management', 38, 'El personal policial que vaya a efectuar tareas de protección deberá disponer de la información actualizada de la víctima y del autor, con los datos más relevantes y hechos significativos del Caso.',
    'Officers carrying out protection must have updated case information.', 'mandatory')
add(2025, 'medium', 'victim_operational', 39, 'Entrevista personal con la víctima.', 'Personal interview.', 'mandatory')
add(2025, 'medium', 'victim_operational', 39, 'Si procede, efectuar traslado de la víctima para su ingreso en un centro de acogida.', 'If appropriate, shelter.', 'conditional_judgement', owner='police_unit_and_victim')
add(2025, 'medium', 'victim_operational', 39, 'Vigilancia ocasional y aleatoria de la víctima en domicilio, lugar de trabajo y centros escolares de los menores en horarios de entrada y salida.',
    'Occasional and random surveillance at home, work and schools.', 'mandatory')
add(2025, 'medium', 'victim_operational', 39, 'Acompañamiento a la víctima en actuaciones de carácter judicial, asistencial o administrativo, cuando se considere que puede existir algún tipo de riesgo para ella.',
    'Accompaniment when a risk is considered to exist.', 'conditional_judgement')
add(2025, 'medium', 'victim_information', 39, 'Recomendar a la víctima el bloqueo de perfiles que puedan ser usados por el agresor para acceder a su perfil o contactar con ella.',
    'Recommend blocking profiles; report and preserve offensive messages.', 'advice_to_victim', owner='victim')
add(2025, 'medium', 'aggressor', 39, 'Comprobación periódica del cumplimiento por el autor de las medidas judiciales de protección impuestas.',
    'Periodic compliance checks (no explicit checks at his home/work).', 'mandatory')
add(2025, 'medium', 'aggressor', 39, 'Comunicación/entrevista con el autor durante permisos penitenciarios y/o excarcelaciones para informarle de que su Caso se encuentra sometido a control/protección policial',
    'Contact the aggressor on prison leave/release.', 'conditional_fact', condition='prison leave or release')
add(2025, 'medium', 'special_relevance', 39, 'Solicitar a Fiscalía el seguimiento obligatorio del autor a través de la asignación de un dispositivo telemático de control.',
    'Ask the prosecutor for electronic monitoring: at Medio ONLY in special-relevance cases.', 'request_other_authority', owner='prosecutor_and_court', condition='special-relevance case')
add(2025, 'high', 'victim_operational', 39, 'En caso de no haberse podido localizar todavía al autor, hablar con la víctima sobre la posibilidad de ser trasladada a casa de un familiar, domicilio distinto o centro de acogida.',
    'If the aggressor is not yet located, DISCUSS relocation with the victim.', 'conditional_fact', owner='victim', condition='aggressor not yet located')
add(2025, 'high', 'victim_information', 39, 'Recomendar a la víctima la eliminación de los perfiles actuales de las redes sociales y el cambio de número de teléfono, que deberá compartir solo con su Círculo de Fortaleza.',
    'Recommend deleting social-media profiles and changing phone number.', 'advice_to_victim', owner='victim')
add(2025, 'high', 'aggressor', 39, 'Entrevista ocasional con el autor.', 'Occasional interview with the aggressor.', 'mandatory')
add(2025, 'high', 'aggressor', 39, 'Vigilancia aleatoria y frecuente de los movimientos del autor.', 'Random and FREQUENT surveillance of the aggressor\'s movements.', 'mandatory')
add(2025, 'high', 'aggressor', 39, 'Solicitar a Fiscalía el seguimiento obligatorio del autor a través de la asignación de un dispositivo telemático de control.',
    'Ask the prosecutor for electronic monitoring (all Alto+ cases).', 'request_other_authority', owner='prosecutor_and_court')
add(2025, 'extreme', 'victim_operational', 40, 'Protección permanente de la víctima hasta que el autor o sus circunstancias dejen de ser una amenaza inminente, realizándose dicha protección de manera presencial por parte del Cuerpo Policial respectivo.',
    'Permanent, in-person protection until the threat is no longer imminent.', 'mandatory')
add(2025, 'extreme', 'victim_operational', 40, 'Vigilancia en centros escolares de los hijos e hijas de la víctima a la hora de entrada y salida.',
    'School surveillance (no longer "si procede").', 'mandatory')
add(2025, 'extreme', 'victim_information', 40, 'Aconsejar a la víctima la creación de una nueva identidad digital.', 'Advise a new digital identity.', 'advice_to_victim', owner='victim')
add(2025, 'extreme', 'aggressor', 40, 'Control intensivo de los movimientos del autor hasta que este deje de ser una amenaza inminente para la seguridad de la víctima.',
    'Intensive control of the aggressor\'s movements.', 'mandatory')
add(2025, 'minors', 'minors', 40, 'Solicitar información a la víctima de la situación en la que se encuentran los menores, resoluciones judiciales sobre custodia, domicilios donde pernoctan, centros educativos a los que acuden; prestando la protección adecuada acorde a cada situación.',
    'Ask about the children\'s situation (custody, where they sleep, schools) and protect accordingly.', 'mandatory', condition='victim has minors in her care')
add(2025, 'minors', 'minors', 40, 'Pedir información a Servicios Sociales sobre lo concerniente al Caso y la situación de los menores.',
    'Ask social services about the case and the children.', 'request_other_authority', owner='police_unit', condition='victim has minors in her care')
add(2025, 'minors', 'minors', 40, 'Acompañamiento a los puntos de encuentro, solicitando información a los educadores/monitores en relación cada Caso.',
    'Accompany to contact centres; ask staff.', 'mandatory', condition='victim has minors in her care')
add(2025, 'minors', 'minors', 40, 'Indagar sobre el posible maltrato a los menores, la existencia de amenazas a la integridad física por parte del presunto agresor, o si la víctima teme por la seguridad del menor.',
    'Inquire into possible abuse of the children; if indications, ask schools/health/social services and inform court/prosecutor.', 'mandatory', condition='victim has minors in her care')
add(2025, 'minors', 'minors', 40, 'Incidir en la percepción de riesgo de la víctima, explicando a la misma cómo los aprendizajes directos o indirectos de conductas violentas en el contexto familiar, pueden perjudicar el natural desarrollo de los menores.',
    'Work on the victim\'s risk perception regarding the children.', 'mandatory', condition='victim has minors in her care')
add(2025, 'minors', 'minors', 40, 'Establecer contactos frecuentes con personal policial tutor.',
    'Frequent contact with the school-liaison police officer.', 'mandatory', condition='victim has minors in her care')

MEASURES = M

# Paired comparison of the measures whose wording or scope differs (each pair cites both measure_ids).
MEASURE_CHANGES = [
    ('aggressor_notified_case_under_control', 'A1-2019-09', 'A2-2025-15', 'narrowed',
     '2019: every bajo+ case. 2025: only "EN EL CASO DE EXISTENCIA DE MEDIDAS JUDICIALES" (and §5.2, persistent aggressors).'),
    ('prison_information_review', 'A1-2019-12', 'A2-2025-17', 'narrowed_and_extended',
     '2019: all bajo+. 2025: only with judicial measures, but adds informing the victim of leave/release.'),
    ('weapons_licence', 'A1-2019-10', 'A2-2025-14', 'narrowed',
     '2025 drops "Posteriormente solicitar la retirada judicial de ambas".'),
    ('referral_to_support_services', 'A1-2019-06', 'A2-2025-07', 'weakened',
     '2019: "Derivación" (referral). 2025: "Información y, en su caso, derivación" (information; referral where appropriate).'),
    ('contact_modality', 'A1-2019-07', 'A2-2025-09', 'resource_contingency_explicit',
     '2019: phone and/or personal, uniform choice agreed with the victim. 2025: personal or phone "en función de los medios disponibles"; plain clothes by default.'),
    ('telematic_device_request', 'A1-2019-18', 'A2-2025-26', 'narrowed_at_medium',
     '2019: requested for every medio (hence alto, extremo) case. 2025: medio only if special relevance; alto+ always.'),
    ('victim_site_surveillance_high', 'A1-2019-22', '', 'removed_at_high',
     '2019 Alto: frequent and random checks at home/work. 2025 Alto lists none; only Medio\'s "vigilancia ocasional y aleatoria" carries over cumulatively.'),
    ('aggressor_surveillance_high', 'A1-2019-23', 'A2-2025-30', 'intensified',
     '2019: random control + sporadic contacts with his circle. 2025: random AND frequent surveillance, plus an occasional interview with him.'),
    ('relocation_high', 'A1-2019-21', 'A2-2025-27', 'softened',
     '2019: "insistir" on relocation. 2025: "hablar con la víctima sobre la posibilidad".'),
    ('aggressor_compliance_checks_medium', 'A1-2019-19', 'A2-2025-24', 'narrowed',
     '2019 includes occasional checks on the aggressor at home/work; 2025 states periodic compliance checks only.'),
    ('permanent_protection_extreme', 'A1-2019-24', 'A2-2025-32', 'specified',
     '2025 adds "de manera presencial por parte del Cuerpo Policial respectivo".'),
    ('school_surveillance_extreme', 'A1-2019-25', 'A2-2025-33', 'strengthened',
     '2019: "Si procede". 2025: unconditional.'),
    ('dossier_to_patrols', 'A1-2019-13', '', 'removed', '2019 optional circulation of the case dossier to patrols; absent from 2025 Annex II.'),
    ('digital_self_protection', '', 'A2-2025-12', 'new', '2025 adds cybersecurity advice at every level (block, delete, new digital identity).'),
    ('minors_block', '', 'A2-2025-36', 'new', '2025 adds a six-item block for victims with minors in their care (all levels).'),
    ('measure_recording', '', '', 'new_weak_duty',
     '2025 Annex II header: recording measures in the system is only "recomendable", "en la medida de lo posible" (C25-A2-REC).'),
]
