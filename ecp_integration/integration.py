import logging
from urllib.parse import urljoin
import requests

from appconf.manager import SettingManager
import simplejson as json

from ecp_integration.sql_func import get_doctors_rmis_location_by_research
from laboratory.utils import current_time
from rmis_integration.client import Settings
from utils.dates import normalize_dash_date
from django.core.cache import cache
from laboratory.settings import RMIS_PROXY
from datetime import timedelta

logger = logging.getLogger(__name__)


def get_url_ecp(path, query=""):
    if query is None:
        query = {}
    return urljoin(SettingManager.get("ecp_api_url", default='http://localhost/', default_type='s'), path) + (f'?{query}')


def get_headers_ecp(sess_id):
    return {'Authorization': f'Basic {sess_id}', 'Cookie': f'PHPSESSID={sess_id}'}


def make_request_get(path, query="", sess_id="", method="GET", get_sess_id=False):
    if query is None:
        query = {}
    try:
        url = get_url_ecp(path, query=query)
        headers = get_headers_ecp(sess_id)
        data = requests.request(method, url, headers=headers, proxies=RMIS_PROXY)
        if get_sess_id:
            return json.loads(data.content.decode()).get("sess_id")
        else:
            return json.loads(data.content.decode())
    except Exception as e:
        logger.exception(e)
        return {}


def request_get_sess_id():
    login = Settings.get("login")
    password = Settings.get("password")
    data = make_request_get("user/login", query=f"Login={login}&Password={password}", get_sess_id=True)
    return data


def get_reserves_ecp(date, med_staff_fact_id):
    sess_id = request_get_sess_id()
    time_end = f"{date} 23:00:00"
    time_start = f"{date} 06:00:00"
    result = make_request_get(
        "TimeTableGraf/TimeTableGrafbyMedStaffFact",
        query=f"Sess_id={sess_id}&MedStaffFact_id={med_staff_fact_id}&TimeTableGraf_end={time_end}&TimeTableGraf_beg={time_start}",
        sess_id=sess_id,
    )
    time_table = []
    for r in result.get('data'):
        cache_key = f"ecp-fio:{r['Person_id']}"
        fio = cache.get(cache_key)
        if not fio:
            patient = make_request_get("Person", query=f"Sess_id={sess_id}&Person_id={r['Person_id']}", sess_id=sess_id)
            data_patient = patient.get('data')
            fio_parts = [
                data_patient[0].get('PersonSurName_SurName'),
                data_patient[0].get('PersonFirName_FirName'),
                data_patient[0].get('PersonSecName_SecName'),
            ]
            fio = " ".join([part for part in fio_parts if part])
            cache.set(cache_key, fio, 60 * 60 * 6)
        time_table.append(
            {
                "uid": r["Person_id"],
                "patient": fio,
                "slot": r["TimeTableGraf_id"],
                "timeStart": r["TimeTableGraf_begTime"].split(" ")[1][:5],
                "timeEnd": r["TimeTableGraf_begTime"].split(" ")[1][:5],
            }
        )
    return sorted(time_table, key=lambda k: k['timeStart'])


def get_slot_ecp(person_id, slot_id):
    sess_id = request_get_sess_id()
    req_result = make_request_get("TimeTableGraf/TimeTableGrafStatus", query=f"Sess_id={sess_id}&Person_id={person_id}&TimeTableGraf_id={slot_id}", sess_id=sess_id)
    d = req_result['data'][0]
    req_result = make_request_get("TimeTableGraf/TimeTableGrafById", query=f"Sess_id={sess_id}&TimeTableGraf_id={slot_id}", sess_id=sess_id)
    r = req_result['data'][0]
    date_time_data = r["TimeTableGraf_begTime"].split(" ")
    dash_date = normalize_dash_date(date_time_data[0])
    date_time = date_time_data[1][:5]
    return (
        {
            "status": d["EvnStatus_id"],
            "datetime": f"{dash_date} {date_time}",
        }
        if d
        else {}
    )


def search_patient_ecp_by_person_id(person_id):
    sess_id = request_get_sess_id()
    result = make_request_get("Person", query=f"Sess_id={sess_id}&Person_id={person_id}", sess_id=sess_id)
    patient = result['data'][0]
    patient_snils = patient.get("PersonSnils_Snils", "")
    result = make_request_get(
        "PersonList",
        query=f"Sess_id={sess_id}&"
        f"PersonSurName_SurName={patient['PersonSurName_SurName']}&"
        f"PersonFirName_FirName={patient['PersonFirName_FirName']}&"
        f"PersonBirthDay_BirthDay={patient['PersonBirthDay_BirthDay']}&PersonSnils_Snils={patient_snils}",
        sess_id=sess_id,
    )
    individual = result['data'][0]
    if individual['Person_id'] == patient['Person_id'] and individual['PolisType_id'] in ['2', '4']:
        patient['enp'] = individual['Polis_Num']
    return patient


def get_doctors_ecp_free_dates_by_research(research_pk, date_start, date_end, hospital_id):
    doctors = get_doctors_rmis_location_by_research(research_pk, hospital_id)
    doctors_has_free_date = {}
    unique_date = []
    for d in doctors:
        sess_id = request_get_sess_id()
        req_result = make_request_get(
            "TimeTableGraf/TimeTableGrafFreeDate", query=f"Sess_id={sess_id}&MedStaffFact_id={d.rmis_location}&TimeTableGraf_beg={date_start}&TimeTableGraf_end={date_end}", sess_id=sess_id
        )
        schedule_data = req_result['data']
        if len(schedule_data) > 0:
            doctors_has_free_date[d.rmis_location] = {"fio": f"{d.family} {d.name} {d.patronymic}", "pk": d.id, "dates": []}
            doctors_has_free_date[d.rmis_location]["dates"] = [s["TimeTableGraf_begTime"] for s in schedule_data]
            unique_date.extend(doctors_has_free_date[d.rmis_location]["dates"])

    return {"doctors_has_free_date": doctors_has_free_date, "unique_date": sorted(set(unique_date))}


def get_doctor_ecp_free_slots_by_date(rmis_location, date):
    sess_id = request_get_sess_id()
    req_result = make_request_get("TimeTableGraf/TimeTableGrafFreeTime", query=f"Sess_id={sess_id}&MedStaffFact_id={rmis_location}&TimeTableGraf_begTime={date}", sess_id=sess_id)
    free_slots = req_result['data']
    if len(free_slots) > 0:
        return sorted(free_slots, key=lambda k: k['TimeTableGraf_begTime'])
    return []


def register_patient_ecp_slot(patient_ecp_id, slot_id):
    sess_id = request_get_sess_id()
    req_result = make_request_get("TimeTableGraf/TimeTableGrafWrite", query=f"Sess_id={sess_id}&Person_id={patient_ecp_id}&TimeTableGraf_id={slot_id}", sess_id=sess_id, method="POST")
    register_result = req_result['data']
    if req_result['error_code'] == 0 and register_result['TimeTableGraf_id'] == slot_id and patient_ecp_id == register_result['Person_id']:
        return {'register': True}

    return {'register': False, "message": "Неудачная попытка записи"}


def search_patient_ecp_by_fio(patient):
    sess_id = request_get_sess_id()
    result = make_request_get(
        "PersonList",
        query=f"Sess_id={sess_id}&"
        f"PersonSurName_SurName={patient['family']}&"
        f"PersonFirName_FirName={patient['name']}&"
        f"PersonSecName_SecName={patient['patronymic']}&"
        f"PersonBirthDay_BirthDay={patient['birthday']}&PersonSnils_Snils={patient['snils']}",
        sess_id=sess_id,
    )
    individual = result['data'][0]
    return individual['Person_id']


def get_ecp_time_table_list_patient(patient_ecp_id):
    sess_id = request_get_sess_id()
    current_date = current_time()
    start_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date = (current_date + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    req_result = make_request_get("TimeTableListbyPatient", query=f"Sess_id={sess_id}&Person_id={patient_ecp_id}&TimeTable_beg={start_date}&TimeTable_end={end_date}", sess_id=sess_id)
    result_tt = req_result['data']['TimeTable']
    if len(result_tt) > 0:
        return [
            {
                "date": normalize_dash_date(i['TimeTable_begTime'].split(" ")[0])[:8],
                "time": i['TimeTable_begTime'].split(" ")[1][:5],
                "Post_name": i['Post_name'],
                "TimeTable_id": i['TimeTable_id'],
            }
            for i in result_tt
        ]
    return []
