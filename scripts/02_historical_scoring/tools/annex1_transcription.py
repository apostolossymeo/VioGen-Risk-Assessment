"""Hand transcription of Annex 1 (López-Ossorio 2016, pp. 274-275), made from the rendered page images
and checked automatically against the PDF text layer by verify_against_pdf().
Each tuple: (row, page, printed_group, label_es, value_printed).
printed_group: the I-number printed in the cell that spans the row in the table image;
'' = the row sits above a numbered block without an I-number of its own (rows 10, 15, 38)."""
ROWS = [
 (1, 274, 'I1', 'Violencia psicológica (vejaciones, insultos y humillaciones)', '1.428'),
 (2, 274, 'I1', 'Existencia de violencia psicológica grave o muy grave', '1.646'),
 (3, 274, 'I2', 'Violencia física', '0'),
 (4, 274, 'I2', 'Violencia física con/sin lesiones', '0'),
 (5, 274, 'I2', 'Existencia de violencia física grave o muy grave', '2.000'),
 (6, 274, 'I3', 'Violencia sexual', '0'),
 (7, 274, 'I3', 'Violencia sexual con lesiones', '0'),
 (8, 274, 'I3', 'Existencia de violencia sexual grave o muy grave', '3.000'),
 (9, 274, 'I4', 'Reacción defensiva víctima ante agresiones físicas', '0'),
 (10, 274, '', '¿Ha empleado el agresor armas u objetos contra la pareja?', '1.533'),
 (11, 274, 'I5', 'El agresor empleó arma blanca', '4.000'),
 (12, 274, 'I5', 'El agresor empleó arma de fuego', '0'),
 (13, 274, 'I5', 'El agresor empleó otros objetos', '0'),
 (14, 274, 'I6', 'El agresor tiene acceso a armas de fuego', '0'),
 (15, 274, '', '¿La víctima recibe o ha recibido amenazas o planes dirigidos a causar daño físico/psicológico?', '0'),
 (16, 274, 'I7', 'Amenazas graves dirigidas a causar daño', '1.893'),
 (17, 274, 'I7', 'Amenazas de suicidio por parte del agresor', '2.049'),
 (18, 274, 'I7', 'Amenazas económicas por parte del agresor', '0'),
 (19, 274, 'I7', 'Amenazas de muerte por parte del agresor', '2.800'),
 (20, 274, 'I7', 'Amenazas a la reputación social de la víctima por parte del agresor', '0'),
 (21, 274, 'I7', 'Amenazas a la integridad/custodia de los hijos', '0'),
 (22, 274, 'I8', '¿Ha existido una escalada en la gravedad y/o la frecuencia de las agresiones o las amenazas de violencia en los últimos seis meses?', '2.800'),
 (23, 274, 'I9', 'En los últimos 6 meses el agresor muestra celos exagerados o sospechas de infidelidad', '3.540'),
 (24, 274, 'I10', 'En los últimos 6 meses el agresor muestra conductas de control', '2.184'),
 (25, 274, 'I10', 'En los últimos 6 meses el agresor muestra conductas de control físico', '1.689'),
 (26, 274, 'I10', 'En los últimos 6 meses el agresor muestra conductas de control psicológico', '1.665'),
 (27, 274, 'I10', 'En los últimos 6 meses el agresor muestra conductas de control escolar/laboral', '2.087'),
 (28, 274, 'I10', 'En los últimos 6 meses el agresor muestra conductas de control económico', '0'),
 (29, 274, 'I10', 'En los últimos 6 meses el agresor muestra conductas de control cibernético', '1.578'),
 (30, 275, 'I11', 'En los últimos 6 meses el agresor muestra acoso', '4.940'),
 (31, 275, 'I12', 'En el último año el agresor produce daños materiales', '0'),
 (32, 275, 'I13', 'En el último año el agresor falta respeto a la autoridad', '1.892'),
 (33, 275, 'I14', 'En el último año agrede físicamente a terceros y/o animales', '3.830'),
 (34, 275, 'I15', 'En el último año existen enfrentamientos físicos o verbales con terceras personas', '1.466'),
 (35, 275, 'I16', 'En los últimos seis meses, ¿existen indicios de problemas en la vida del agresor?', '1.628'),
 (36, 275, 'I16', 'Existencia de problemas laborales/económicos del agresor en los últimos 6 meses', '0'),
 (37, 275, 'I16', 'Existencia de problemas del agresor con la justicia en los últimos 6 meses', '0'),
 (38, 275, '', 'Existen antecedentes penales/policiales del agresor', '2.142'),
 (39, 275, 'I17', 'Existen quebrantamientos previos (cautelares/penales)', '2.336'),
 (40, 275, 'I18', 'Existen antecedentes de agresiones físicas/sexuales', '1.870'),
 (41, 275, 'I19', 'Existen antecedentes de violencia de género sobre otras parejas', '1.571'),
 (42, 275, 'I20', 'El agresor presenta un trastorno mental/psiquiátrico', '3.000'),
 (43, 275, 'I21', 'El agresor presenta ideas/intentos de suicidio', '3.890'),
 (44, 275, 'I22', 'El agresor mantiene algún tipo adicción o conductas de abuso (alcohol, drogas y fármacos)', '3.336'),
 (45, 275, 'I23', 'El agresor tiene antecedentes familiares de violencia de género o doméstica', '1.667'),
 (46, 275, 'I24', 'Existencia de algún tipo de discapacidad', '0'),
 (47, 275, 'I25', 'Víctima en periodo de gestación', '0'),
 (48, 275, 'I26', 'Víctima con enfermedad grave', '0'),
 (49, 275, 'I27', 'Víctima extranjera', '0'),
 (50, 275, 'I28', 'Víctima sin apoyo familiar/social', '0'),
 (51, 275, 'I29', 'Víctima con trastorno mental/psiquiátrico', '0'),
 (52, 275, 'I30', 'Víctima con ideas/intentos de suicidio', '0'),
 (53, 275, 'I31', 'La víctima mantiene algún tipo adicción o conductas de abuso (alcohol, drogas y fármacos)', '0'),
 (54, 275, 'I32', 'La víctima tiene antecedentes de violencia de género o doméstica', '0'),
 (55, 275, 'I32', 'La víctima tiene antecedentes familiares de violencia de género o doméstica', '0'),
 (56, 275, 'I33', 'La víctima depende económicamente del agresor', '0'),
 (57, 275, 'I34', 'La víctima tiene a su cargo menores de edad o familiares', '0'),
 (58, 275, 'I35', 'La víctima ha denunciado a otros agresores en el pasado', '0'),
 (59, 275, 'I35', 'La víctima ha retirado denuncias en el pasado', '0'),
 (60, 275, 'I36', 'La víctima ha expresado al agresor su intención de romper hace menos de 6 meses', '3.286'),
 (61, 275, 'I37', 'Se han registrado episodios de violencia recíproca', '0'),
 (62, 275, 'I38', 'La víctima teme por la integridad de los menores o familiares a su cargo', '1.443'),
 (63, 275, 'I39', 'La víctima piensa que el agresor es capaz de agredirla con mucha violencia o incluso matarla', '2.830'),
]

def _norm(s):
    import re
    return re.sub(r'\s+', ' ', s).strip()

def verify_against_pdf(pdf_path):
    """Every label must occur in its page's text layer (whitespace-normalised) and the printed values,
    read top to bottom in the right-hand column, must equal the transcription's values in order."""
    import pymupdf, re
    doc = pymupdf.open(pdf_path)
    report = []
    for page in (274, 275):
        pg = doc[page - 1]
        text = _norm(pg.get_text())
        vals = [w for w in pg.get_text('words') if w[0] > 450 and re.fullmatch(r'\d\.\d{3}|0', w[4])]
        vals = [w[4] for w in sorted(vals, key=lambda w: (w[1] + w[3]) / 2)]
        mine = [r for r in ROWS if r[1] == page]
        for r in mine:
            report.append(dict(row=r[0], page=page, label_found_in_pdf_text=_norm(r[3]) in text))
        report.append(dict(row=f'values p.{page}', page=page,
                           label_found_in_pdf_text=vals == [r[4] for r in mine]))
    return report
