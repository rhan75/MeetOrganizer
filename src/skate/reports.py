from sqlalchemy.engine.base import Engine
import pandas as pd
# from weasyprint import HTML

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

#Generate list of record for the event
def generate_event_schedule_list_repport(meet_ID: int, event: int, report_path: str, division_range: tuple, engine: Engine) -> None:
    genders = [1, 2]
    low_div = division_range[0]
    high_div = division_range[1]
    for gender_ID in genders:
        qry = (
        f'select skater.club_member_number as "ID", skater.first_name, skater.last_name, club.abbreviation as "Aff", rhrd.time '
        f'from "Race_Heat_Result_Detail" as rhrd '
        f'left join "Race_Heat_Result" as rhr '
        f'on rhrd."rhr_ID" = rhr."rhr_ID" '
        f'left join  "Race_Heat_Schedule" as rhs '
        f'on rhs."rhs_ID" = rhr."rhs_ID" '
        f'left join "Skater" as skater '
        f'on skater."skater_ID" = rhrd."skater_ID" '
        f'left join "Club" as club '
        f'on club."club_ID" = skater."club_ID" '
        f'where event = {event} and "meet_ID" = {meet_ID} and "division_ID" between {low_div} and {high_div} and skater."gender_ID" = {gender_ID} order by time desc;'
        )
        skaters = pd.read_sql_query(qry, engine)
        report_name = f'event_{event}_schedule_list_division-{low_div}-2-{high_div}-{gender_ID}'
        generate_report(report_name, report_path, skaters)

def generate_division_report_name(meet_ID: int, division_ID: int, race_ID: int, gender_ID: int, engine: Engine) -> str:
    #find rdr_ID using meet_ID, division_ID, race_ID, gender_ID
    meet = pd.read_sql_query('select * from "Meet";', con=engine)
    race = pd.read_sql_query('select * from "Race";', con=engine)
    division = pd.read_sql_query('select * from "Division";', con=engine)
    gender = pd.read_sql_query('select * from "Gender";', con=engine)
    division_name = division[division['division_ID']== division_ID].iloc[0]['name']
    gender_name = gender[gender['gender_ID']==gender_ID].iloc[0]['name']
    race_name = race[race['race_ID']==race_ID].iloc[0]['name']
    meet_name = meet[meet['meet_ID']==meet_ID].iloc[0]['name']
    return f"{meet_name} {gender_name.upper()} {division_name.upper()} {race_name}"

def generate_division_report(meet_ID: int, event: int, report_path: str, engine: Engine) -> None:
    #find rdr_ID using meet_ID, division_ID, race_ID, gender_ID

    
    qry = (
        f'select distinct rdrd."rdr_ID" '
        f'from "Race_Heat_Result" as rhr '
        f'left join "Race_Heat_Schedule" as rhs '
        f'on rhs."rhs_ID" = rhr."rhs_ID" '
        f'left join "Race_Heat_Result_Detail" as rhrd '
        f'on rhrd."rhr_ID" = rhr."rhr_ID" '
        f'left join "Race_Division_Result_Detail" as rdrd '
        f'on rdrd."rhrd_ID" = rhrd."rhrd_ID" '
        f'where rhs."meet_ID" = {meet_ID} and rhs.event = {event};'
    )
    rdr_ID_df = pd.read_sql_query(qry, engine)
    for idx, rdr in rdr_ID_df.iterrows():
        rdr_ID = rdr[0]
        report_qry = (
            f'select skater.first_name as "First Name", skater.last_name as "Last Name", club.abbreviation as "Club", '
            f'rhrd.time as "Time", rdrd.rank as "Rank", rdrd.score as "Score" '
            f'from "Race_Division_Result_Detail" as rdrd '
            f'left join "Race_Heat_Result_Detail" as rhrd '
            f'on rdrd."rhrd_ID" = rhrd."rhrd_ID" '
            f'left join "Skater" as skater '
            f'on rhrd."skater_ID" = skater."skater_ID" '
            f'left join "Club" as club '
            f'on skater."club_ID" = club."club_ID" '
            f'left join "Race_Heat_Result" as rhr '
            f'on rhr."rhr_ID" = rhrd."rhr_ID" ' 
            f'left join "Race_Heat_Schedule" as rhs ' 
            f'on rhs."rhs_ID" = rhr."rhs_ID" '
            f'where rdrd."rdr_ID" = {rdr_ID} and rhs.event = {event} '
            f'order by rdrd.rank;'     
        )   
        report = pd.read_sql_query(report_qry, con=engine)   
           
        rdr = pd.read_sql_query(f'select * from "Race_Division_Result" where "rdr_ID" = {rdr_ID}', engine)
        race_ID = rdr.iloc[0]['race_ID']
        gender_ID =rdr.iloc[0]['gender_ID'] 
        division_ID = rdr.iloc[0]['division_ID']
        report_name = f'{generate_division_report_name(meet_ID, division_ID, race_ID, gender_ID, engine)}-event_{event}'

        generate_report(report_name, report_path, report)  


def generate_race_heat_report(meet_ID: int, event: int, report_path: str, engine: Engine) -> None:
    rhs_IDs = pd.read_sql_query(f'select "rhs_ID" from "Race_Heat_Schedule" where "meet_ID" = {meet_ID} and event = {event};', engine)
    for idx, row in rhs_IDs.iterrows(): 
        rhs_ID = (row[0])

        qry = (
            f'select skater.club_member_number as "ID", rhrd.rank, skater.first_name, skater.last_name, lane.name, rhrd.time '
            f'from "Race_Heat_Result_Detail" as rhrd '
            f'left join "Race_Heat_Result" as rhr '
            f'on rhrd."rhr_ID" = rhr."rhr_ID" '
            f'left join  "Race_Heat_Schedule" as rhs '
            f'on rhs."rhs_ID" = rhr."rhs_ID" '
            f'left join "Skater" as skater '
            f'on skater."skater_ID" = rhrd."skater_ID" '
            f'left join "Lane" as lane '
            f'on rhrd."lane_ID" = lane."lane_ID" '
            f'where rhs."rhs_ID" = {rhs_ID} order by rank;'
        )
        report = pd.read_sql_query(qry, engine)
        report_name = f'heat_result-event-{event}-{idx}'
        generate_report(report_name, report_path, report)

def generate_meet_division_report(meet_ID: int, report_path: str, engine: Engine) -> None:
    mdr = pd.read_sql_query(f'select distinct "mdr_ID", name from "Meet_Division_Result" where "meet_ID" = {meet_ID}', engine)
    for idx, each_mdr in mdr.iterrows():
        mdr_ID = each_mdr[0]
        report_name = f'Combined_{each_mdr[1]}-{idx}'
        qry = (
            f'select skater.club_member_number as "ID", skater.first_name as "First Name", skater.last_name as "Last Name", '
            f'club.abbreviation as "Club", mdrd.rank as "Rank", mdrd.total_score as "Score" '
            f'from "Meet_Division_Result_Detail" as mdrd '
            f'left join "Skater" as skater '
            f'on mdrd."skater_ID" = skater."skater_ID" '
            f'left join "Club" as club '
            f'on skater."club_ID" = club."club_ID" '
            f'where mdrd."mdr_ID" = {mdr_ID} order by mdrd.rank;'
        )
        report = pd.read_sql_query(qry, con=engine)   
        generate_report(report_name, report_path, report)     
 
