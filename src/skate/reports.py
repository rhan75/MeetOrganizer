from sqlalchemy.engine.base import Engine
import pandas as pd
from sqlalchemy import exists, and_
from sqlalchemy.orm import sessionmaker, aliased
from skate.model import *
from sqlalchemy import select, exists, and_
# from weasyprint import HTML

AG = aliased(Age_Group)
AGC = aliased(Age_Group_Class)

CS = aliased(Competition_Skater)
CAGR = aliased(Competition_Age_Group_Result)
CAGRD = aliased(Competition_Age_Group_Result_Detail)

RHS = aliased(Race_Heat_Schedule)
RHR = aliased(Race_Heat_Result)
RHRD = aliased(Race_Heat_Result_Detail)
RAGR = aliased(Race_Age_Group_Result)
RHSD = aliased(Race_Heat_Schedule_Detail)
RAGRD = aliased(Race_Age_Group_Result_Detail)
RS = aliased(Race_Style)


def prep_session(engine: Engine) -> sessionmaker:
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
'''
Report Functions
'''
def generate_report(report_name: str, report_path: str, report: pd.DataFrame) -> None:
    html_file = f'{report_path}/{report_name}.html'
    excel_file = f'{report_path}/{report_name}.xlsx'
    report.to_excel(excel_file, index=False)
    html = report.to_html(index=False)
    title = """
        <html>
        <head>
        <style>
        thead {color: green;}
        tbody {color: black;}
        tfoot {color: red;}

        table, th, td {
        border: 1px solid black;
        }
        </style>
        </head>
        <body>

        <h4>
        """ + report_name + "</h4>"

    end_html = """
        </body>
        </html>
        """
    html = title + html + end_html

    with open(html_file, 'w') as file:
        file.write(html)
    # HTML(html_file).write_pdf(pdf_file)

def convert_time_to_string(time_value):
    if time_value is None:
        return None
    return time_value.strftime('%M:%S.%f')[:-3]

#Generate list of record for the event
def generate_event_schedule_list_report(competition_id: int, event: int, report_path: str, age_group_range: dict, engine: Engine) -> None:
    session = prep_session(engine)
    low_div_name = age_group_range['low_age_group']['name']
    low_div = age_group_range['low_age_group']['ag_id']
    high_div_name = age_group_range['high_age_group']['name']
    high_div = age_group_range['high_age_group']['ag_id']
    reports = pd.DataFrame()
    report_name = f'Event {event} Men and Women Result for Age Group {low_div_name} and {high_div_name} '
    genders = {'Men':1, 'Women': 2}
    report_cols = ['ID', 'Last Name', 'First Name', 'Aff', 'Time']
    report = session.query(Skater.id, Skater.last_name, Skater.first_name, Club.abbreviation, RHRD.time)\
        .outerjoin(RHR, RHR.id == RHRD.rhr_id)\
        .outerjoin(RHS, RHS.id == RHR.rhs_id)\
        .outerjoin(Skater, Skater.id == RHRD.skater_id)\
        .outerjoin(Club, Club.id == Skater.club_id)\
        .filter(and_(RHS.event == event, RHS.competition_id == competition_id, RHRD.ag_id.between(low_div, high_div)))\
        .order_by(RHRD.time.desc())\
        .all()
    report = pd.DataFrame(report, columns=report_cols)
    report['Time'] = report['Time'].apply(convert_time_to_string)
    event_schedule_name = f'Event {event} Result for Age Group {low_div_name}-2-{high_div_name}'
    title_row = pd.DataFrame({'ID': event_schedule_name, 'Last Name':'', 'First Name':'', 'Aff':'', 'Time':''}, index=[0])
    empty_row = pd.DataFrame({col: '' for col in report_cols}, index=[0])
    reports = pd.concat([reports, title_row, report, empty_row], ignore_index=True) 

    for gender_name in genders.keys():
        gender_id = genders[gender_name]
        report = session.query(Skater.id, Skater.last_name, Skater.first_name, Club.abbreviation, RHRD.time)\
            .outerjoin(RHR, RHR.id == RHRD.rhr_id)\
            .outerjoin(RHS, RHS.id == RHR.rhs_id)\
            .outerjoin(Skater, Skater.id == RHRD.skater_id)\
            .outerjoin(Club, Club.id == Skater.club_id)\
            .filter(and_(RHS.event == event, RHS.competition_id == competition_id, Skater.gender_id == gender_id, RHRD.ag_id.between(low_div, high_div)))\
            .order_by(RHRD.time.desc())\
            .all()
        report = pd.DataFrame(report, columns=report_cols)
        report['Time'] = report['Time'].apply(convert_time_to_string)
        # report = pd.read_sql_query(qry, engine)
        event_schedule_name = f'Event {event} Result for Age Group {low_div_name}-2-{high_div_name}-{gender_name}'
        title_row = pd.DataFrame({'ID': event_schedule_name, 'Last Name':'', 'First Name':'', 'Aff':'', 'Time':''}, index=[0])
        empty_row = pd.DataFrame({col: '' for col in report.columns}, index=[0])
        reports = pd.concat([reports, title_row, report, empty_row], ignore_index=True) 
    generate_report(report_name, report_path, reports)

def generate_age_group_report_name(competition_id: int, ag_id: int, race_id: int, gender_id: int, engine: Engine) -> str:
    session = prep_session(engine)
    age_group_name = session.query(AG).where(AG.id == ag_id).first().name
    gender_name = session.query(Gender).where(Gender.id == gender_id).first().name
    race_name = session.query(Race).where(Race.id == race_id).first().name
    competition_name = session.query(Competition).where(Competition.id == competition_id).first().name
    return f"{competition_name} {gender_name.upper()} {age_group_name.upper()} {race_name}"

def generate_age_group_report(competition_id: int, event: int, report_path: str, engine: Engine) -> None:
    session = prep_session(engine)
    #find ragr_id using competition_id, ag_id, race_id, gender_id
    report_name = f'Age Group Results for Event {event}'
    reports = pd.DataFrame()
    ragr_id_df = session.query(RAGRD.ragr_id)\
        .outerjoin(RHRD, RAGRD.rhrd_id == RHRD.id)\
        .outerjoin(RHR, RHRD.rhr_id == RHR.id)\
        .outerjoin(RHS, RHS.id == RHR.rhs_id)\
        .filter(and_(RHS.competition_id == competition_id, RHS.event == event)).distinct().all()
    for row in ragr_id_df:
        ragr_id = row.ragr_id
        report_cols = ['Place', 'ID',"Last Name","First Name", "Aff", "Time","Score" ]

        report = session.query(RAGRD.rank, Skater.club_member_number, Skater.last_name, Skater.first_name, Club.abbreviation, RHRD.time, RAGRD.score)\
            .outerjoin(RHRD, RHRD.id == RAGRD.rhrd_id)\
            .outerjoin(Skater, Skater.id == RHRD.skater_id)\
            .outerjoin(Club, Club.id == Skater.club_id)\
            .outerjoin(RHR, RHR.id == RHRD.rhr_id)\
            .outerjoin(RHS, RHS.id == RHR.rhs_id)\
            .fiter(and_(RAGRD.ragr_id == ragr_id, RHS.event == event)).all()
        report = pd.DataFrame(report, columns=report_cols)
        report['Time'] = report['Time'].apply(convert_time_to_string)
        rdr = session.query(RAGR.race_id, RAGR.gender_id, RAGR.ag_id).where(RAGR.id == ragr_id).first()
        race_id = rdr.race_id
        gender_id =rdr.gender_id
        ag_id = rdr.ag_id
        age_group_result_name = f'{generate_age_group_report_name(competition_id, ag_id, race_id, gender_id, engine)}-event_{event}'
        title_row = pd.DataFrame({'Place': age_group_result_name, 'ID': '', 'Last Name':'', 'First Name':'', 'Aff':'', 'Time':'', 'Score': ''}, index=[0])
        empty_row = pd.DataFrame({col: '' for col in report.columns}, index=[0])
        reports = pd.concat([reports, title_row, report, empty_row], ignore_index=True) 

    generate_report(report_name, report_path, reports)  


def generate_race_heat_report(competition_id: int, event: int, report_path: str, engine: Engine) -> None:
    session = prep_session(engine)
    report_name = f'Event No. {event} Results'
    reports = pd.DataFrame()
    # rhs_ids = pd.read_sql_query(f'select id, name from race_heat_schedule where competition_id = {competition_id} and event = {event};', engine)
    rhs_ids =session.query(RHS.id, RHS.name).where(and_(RHS.competition_id==competition_id, RHS.event==event)).all()
    # for idx, row in rhs_ids.iterrows(): 
    for row in rhs_ids:
        rhs_id = row.id
        name = row.name
        report_lst = session.query(RHRD.rank, Skater.club_member_number, Lane.name, Skater.last_name, Skater.first_name, Club.abbreviation, RHRD.time)\
            .outerjoin(RHR, RHRD.rhr_id==RHR.id).outerjoin(RHS, RHS.id==RHR.rhs_id).outerjoin(Skater, Skater.id==RHRD.skater_id)\
            .outerjoin(Lane, Lane.id==RHRD.lane_id).outerjoin(Club, Club.id == Skater.club_id)\
            .where(RHS.id == rhs_id).order_by(RHRD.rank).all()

        title_row = pd.DataFrame({'Place': name, 'ID': '', 'Lane':'', 'Last Name':'', 'First Name':'', 'Aff':'', 'Time':''}, index=[0])
        report_col = ['Place', 'ID', 'Lane', 'Last Name', 'First Name', 'Aff', 'Time']
        report = pd.DataFrame(report_lst, columns=report_col)
        report['Time'] = report['Time'].apply(convert_time_to_string)
        empty_row = pd.DataFrame({col: '' for col in report.columns}, index=[0])
        reports = pd.concat([reports, title_row, report, empty_row], ignore_index=True)
    generate_report(report_name, report_path, reports)

def generate_competition_age_group_report(competition_id: int, report_path: str, engine: Engine) -> None:
    session = prep_session(engine)
    reports = pd.DataFrame()
    Competition_name = session.query(Competition).where(Competition.id == competition_id).first().name
    report_name = f'Combined Final Report for {Competition_name}'
    cagr = session.query(CAGR.id, CAGR.name).where(CAGR.competition_id == competition_id).distinct().all()
    for row in cagr:
        cagr_id = row.id
        title_row = pd.DataFrame({'Place': row.name, 'ID': '', 'Last Name':'', 'First Name':'', 'Aff':'', 'Total Score':''}, index=[0])
        report_cols = ["Place", "ID", "Last Name", "First Name", "Aff", "Total Score"]
        report = session.query(CAGRD.rank, Skater.club_member_number, Skater.last_name, Skater.first_name, Club.abbreviation, CAGRD.total_score)\
            .outerjoin(Skater, CAGRD.skater_id == Skater.id)\
            .outerjoin(Club, Skater.club_id == Club.id)\
            .filter(CAGRD.cagr_id == cagr_id).order_by(CAGRD.rank).all()
        report = pd.DataFrame(report, columns=report_cols)
        empty_row = pd.DataFrame({col: '' for col in report.columns}, index=[0])
        reports = pd.concat([reports, title_row, report, empty_row], ignore_index=True)
    generate_report(report_name, report_path, reports)     
 
