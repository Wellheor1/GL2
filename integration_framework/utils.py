import datetime

import magic
import pytz
from laboratory import settings
import simplejson as json
from dateutil.relativedelta import relativedelta
import directions.models as directions
from directory.models import Fractions
from laboratory.settings import (
    DEATH_RESEARCH_PK,
    DEF_LABORATORY_AUTH_PK,
    DEF_LABORATORY_LEGAL_AUTH_PK,
)

from results.sql_func import get_paraclinic_results_by_direction, get_laboratory_results_by_directions
from users.models import DoctorProfile
from utils.dates import normalize_dots_date
from directions.models import Napravleniya
from utils.nsi_directories import NSI


def get_json_protocol_data(pk):
    result_protocol = get_paraclinic_results_by_direction(pk)
    data = {}
    document = {}
    for r in result_protocol:
        if "{" in r.value and "}" in r.value:
            try:
                val = json.loads(r.value)
                if not val or not isinstance(val, dict):
                    pass
            except Exception:
                val = r.value
        else:
            val = r.value
        if "rows" in val:
            for k in val['rows']:
                count = 0
                for el in k:
                    if "{" in el and "}" in el:
                        try:
                            el = json.loads(el)
                            if not el or not isinstance(el, dict):
                                pass
                            else:
                                k[count] = el
                        except Exception:
                            pass
                    count += 1
        if isinstance(val, str):
            if val.strip() in ('-', ''):
                val = ""
        if r.title == "Страховая ОМС":
            nsi_smo_code = NSI.get("1.2.643.5.1.13.13.99.2.183_smo_id", None)
            if val and nsi_smo_code:
                smo_id = nsi_smo_code["values"][val.get("code", "")]
                val["id"] = smo_id

        data[r.title] = val

    iss = directions.Issledovaniya.objects.get(napravleniye_id=pk)
    if iss.research_id == DEATH_RESEARCH_PK:
        data_direct_death = data.get("а) Болезнь или состояние, непосредственно приведшее к смерти", None)
        if data_direct_death:
            period_befor_death = data_direct_death["rows"][0][0]
            type_period_befor_death = data_direct_death["rows"][0][1]
            date_death = data["Дата смерти"]
            time_death = data.get("Время смерти", "00:00")
            if period_befor_death and type_period_befor_death:
                data["Начало патологии"] = start_pathological_process(f"{date_death} {time_death}", int(period_befor_death), type_period_befor_death)
    doctor_confirm_obj = iss.doc_confirmation
    author_data = author_doctor(doctor_confirm_obj)

    legal_auth = data.get("Подпись от организации", None)
    legal_auth_data = legal_auth_get(legal_auth)
    hosp_obj = doctor_confirm_obj.hospital
    hosp_oid = hosp_obj.oid

    document["id"] = pk
    time_confirm = iss.time_confirmation
    confirmed_time = time_confirm.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%Y%m%d%H%M')
    document["confirmedAt"] = f"{confirmed_time}+0800"
    document["legalAuthenticator"] = legal_auth_data
    document["author"] = author_data
    document["content"] = data
    document["content"]["Код ОКПО"] = hosp_obj.okpo
    document["oidMo"] = hosp_oid
    document["organization"] = organization_get(hosp_obj)
    document["orgName"] = hosp_obj.title
    document["tel"] = hosp_obj.phones

    return document


def get_json_labortory_data(pk):
    result_protocol = get_laboratory_results_by_directions([pk])
    document = {}
    confirmed_at = ""
    date_reiceve = ""
    data = []
    prev_research_title = ""
    count = 0
    tests = []
    author_data = None
    iss = None
    for k in result_protocol:
        iss = directions.Issledovaniya.objects.get(pk=k.iss_id)
        next_research_title = iss.research.title
        if (prev_research_title != next_research_title) and count != 0:
            if len(tests) > 0:
                data.append({"title": prev_research_title, "tests": tests, "confirmedAt": confirmed_at, "receivedAt": date_reiceve, "author_data": author_data})
            tests = []
        author_data = author_doctor(iss.doc_confirmation)
        time_confirm = iss.time_confirmation
        confirmed_time = time_confirm.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%Y%m%d%H%M')
        fraction_id = k.fraction_id
        frac_obj = Fractions.objects.get(pk=fraction_id)
        if not frac_obj.unit or not frac_obj.fsli:
            continue
        unit_obj = frac_obj.unit
        unit_val = {"code": unit_obj.code, "full_title": unit_obj.title, "ucum": unit_obj.ucum, "short_title": unit_obj.short_title}
        flsi_param = {"code": frac_obj.fsli, "title": frac_obj.title}
        result_val = k.value.replace(",", ".") if k.value else ""
        confirmed_at = f"{confirmed_time}+0800"
        date_reiceve = normalize_dots_date(k.date_confirm).replace("-", "")
        date_reiceve = f"{date_reiceve}0800+0800"
        tests.append({"unit_val": unit_val, "flsi_param": flsi_param, "result_val": result_val})
        prev_research_title = next_research_title
        count += 1
    if len(tests) > 0:
        data.append({"title": prev_research_title, "tests": tests, "confirmedAt": confirmed_at, "receivedAt": date_reiceve, "author_data": author_data})

    hosp_obj = iss.doc_confirmation.hospital
    hosp_oid = hosp_obj.oid

    document["id"] = pk
    legal_auth_data = legal_auth_get({"id": iss.legal_authenticator_id})
    document["legalAuthenticator"] = legal_auth_data
    document["author"] = author_data
    document["content"] = {}
    document["content"]["Лаборатория"] = data
    document["content"]["Код ОКПО"] = hosp_obj.okpo
    document["content"]["payment"] = {"code": "1", "title": "Средства обязательного медицинского страхования"}
    document["oidMo"] = hosp_oid
    document["orgName"] = hosp_obj.title
    direction_obj = Napravleniya.objects.get(pk=pk)
    direction_create = direction_obj.data_sozdaniya
    direction_create = direction_create.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%Y%m%d%H%M')
    document["createdAt"] = f"{direction_create}+0800"
    document["lastConfirmedAt"] = f"{confirmed_at}"
    document["confirmedAt"] = f"{confirmed_at}"
    document["organization"] = organization_get(hosp_obj)

    return document


def organization_get(hosp_obj_f):
    return {
        "name": hosp_obj_f.title,
        "tel": hosp_obj_f.phones if hosp_obj_f.phones else "",
        "address": {
            "text": hosp_obj_f.address if hosp_obj_f.address else "г. Иркутск",
            "subjectCode": "38",
            "subjectName": "Иркутская область",
        },
    }


def author_doctor(doctor_confirm_obj, is_recursion=False):
    author = {}
    author["id"] = doctor_confirm_obj.pk
    author["positionCode"] = doctor_confirm_obj.position.n3_id if doctor_confirm_obj.position else ""
    author["positionName"] = doctor_confirm_obj.position.title if doctor_confirm_obj.position else ""
    author["snils"] = doctor_confirm_obj.snils if doctor_confirm_obj.snils else ""
    if "" in [author["positionCode"], author["positionName"], author["snils"]] and DEF_LABORATORY_AUTH_PK and not is_recursion:
        return author_doctor(DoctorProfile.objects.get(pk=DEF_LABORATORY_AUTH_PK), True)
    author["name"] = {}
    author["name"]["family"] = doctor_confirm_obj.family
    author["name"]["name"] = doctor_confirm_obj.name
    author["name"]["patronymic"] = doctor_confirm_obj.patronymic
    return author


def legal_auth_get(legal_auth_doc, is_recursion=False):
    legal_auth = {"id": "", "snils": "", "positionCode": "", "positionName": "", "name": {"family": "", "name": "", "patronymic": ""}}
    if legal_auth_doc and legal_auth_doc["id"]:
        id_doc = legal_auth_doc["id"]
        legal_doctor = DoctorProfile.objects.get(pk=id_doc)
        legal_auth["id"] = legal_doctor.pk
        legal_auth["snils"] = legal_doctor.snils
        legal_auth["positionCode"] = legal_doctor.position.n3_id
        legal_auth["positionName"] = legal_doctor.position.title
        legal_auth["name"]["family"] = legal_doctor.family
        legal_auth["name"]["name"] = legal_doctor.name
        legal_auth["name"]["patronymic"] = legal_doctor.patronymic
    if (legal_auth["positionCode"] not in [7] or "" in [legal_auth["positionCode"], legal_auth["positionName"], legal_auth["snils"]]) and DEF_LABORATORY_LEGAL_AUTH_PK and not is_recursion:
        return legal_auth_get({"id": DEF_LABORATORY_LEGAL_AUTH_PK}, True)
    return legal_auth


def start_pathological_process(date_death, time_data, type_period):
    dt = datetime.datetime.strptime(date_death, '%Y-%m-%d %H:%M')
    period = {
        "часов": relativedelta(hours=-time_data),
        "минут": relativedelta(minutes=-time_data),
        "дней": relativedelta(days=-time_data),
        "суток": relativedelta(days=-time_data),
        "месяцев": relativedelta(months=-time_data),
        "лет": relativedelta(years=-time_data),
    }
    delta = dt + period[type_period]
    delta.strftime("%Y%m%d%H:%M:%S")
    return f"{delta.strftime('%Y%m%d%H%M')}+0800"


def check_type_file(file):
    type_file = magic.from_buffer(open(file).read(2048))
    if "pdf" in type_file.lower() or "jpeg" in type_file.lower():
        return True
    return False

