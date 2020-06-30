from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm
from copy import deepcopy
from reportlab.lib.enums import TA_JUSTIFY
import directory.models as directory
from directions.models import ParaclinicResult
from utils.dates import normalize_date
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from api.directions.views import directions_anesthesia_load
import simplejson as json
from django.http import HttpRequest


def form_01(direction, iss, fwb, doc, leftnone, user=None):
    # Форма для печати наркозной карты - течения Анестези при операции

    styleSheet = getSampleStyleSheet()
    style = styleSheet["Normal"]
    style.fontName = "FreeSans"
    style.fontSize = 9
    style.alignment = TA_JUSTIFY
    style_ml = deepcopy(style)
    style_ml.leftIndent = 5 * mm
    styleBold = deepcopy(style)
    styleBold.fontName = "FreeSansBold"

    styleTC = deepcopy(style)
    styleTC.fontSize = 8

    txt = ''
    for group in directory.ParaclinicInputGroups.objects.filter(research=iss.research).order_by("order"):
        results = ParaclinicResult.objects.filter(issledovaniye=iss, field__group=group).exclude(value="").order_by("field__order")
        if results.exists():
            if group.show_title and group.title != "":
                txt += "<font face=\"FreeSansBold\">{}:</font>&nbsp;".format(group.title.replace('<', '&lt;').replace('>', '&gt;'))
            vals = []
            for r in results:
                field_type = r.get_field_type()
                v = r.value.replace('<', '&lt;').replace('>', '&gt;').replace("\n", "<br/>")
                v = v.replace('&lt;sub&gt;', '<sub>')
                v = v.replace('&lt;/sub&gt;', '</sub>')
                v = v.replace('&lt;sup&gt;', '<sup>')
                v = v.replace('&lt;/sup&gt;', '</sup>')

                if field_type == 21:
                    fwb.append(Paragraph(txt, style))
                    txt = ''
                    query_anesthesia = json.dumps({"research_data": {"iss_pk": iss.pk, "field_pk": r.field.pk}})
                    query_obj = HttpRequest()
                    query_obj._body = query_anesthesia
                    query_obj.user = user
                    results = directions_anesthesia_load(query_obj)
                    results_json = json.loads(results.content.decode('utf-8'))
                    step = 0
                    opinion = []
                    cols_count = 0
                    for record in results_json['data']:
                        if step == 0:
                            temp_record = [Paragraph('{} {}'.format(el[11:16], normalize_date(el[0:10])[0:5]), styleBold) for el in record]
                            temp_record[0] = Paragraph('{}'.format(record[0]), styleBold)
                            cols_count = len(temp_record)
                        else:
                            temp_record = [Paragraph('{}'.format(el), styleTC) for el in record]
                        opinion.append(temp_record)
                        step += 1
                    cols_width = [13 * mm for i in range(cols_count)]
                    cols_width[0] = 35 * mm
                    cols_width[-1] = 15 * mm

                    tbl = Table(opinion, repeatRows=1, colWidths=cols_width, hAlign='LEFT')

                    tbl.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1.0, colors.black),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 1 * mm),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))

                    fwb.append(tbl)
                    fwb.append(Spacer(1, 1 * mm))
                    continue

                if field_type == 1:
                    vv = v.split('-')
                    if len(vv) == 3:
                        v = "{}.{}.{}".format(vv[2], vv[1], vv[0])
                if field_type in [11, 13]:
                    v = '<font face="FreeSans" size="8">{}</font>'.format(v.replace("&lt;br/&gt;", " "))

                if r.field.get_title(force_type=field_type) != "":
                    vals.append("{}:&nbsp;{}".format(r.field.get_title().replace('<', '&lt;').replace('>', '&gt;'), v))
                else:
                    vals.append(v)
            txt += "; ".join(vals)
            txt = txt.strip()
            if len(txt) > 0 and txt.strip()[-1] != ".":
                txt += ". "
            elif len(txt) > 0:
                txt += " "

    fwb.append(Paragraph(txt, style))

    return fwb


def form_02():
    # Форма для печати реанимационной карты - за 1 день
    return ''