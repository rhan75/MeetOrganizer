from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Time, Float, ForeignKey, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
import pandas as pd
from datetime import timedelta, date 
from weasyprint import HTML

def find_skating_age(dob: date) -> int:
    current_date = date.today()
    if current_date.month > 7:
        skating_year = current_date.year
    else:
        skating_year = current_date.year - 1
    skating_age_date = date(skating_year, 6, 30)
    return int(int((skating_age_date - dob).days) / 365.2425)

def find_schedule_info(race_info: str) -> dict:  # Checked
    schedule_info = {}
    schedule_info['heat'] = race_info.split(',')[1]
    schedule_info['round'] = race_info.split(',')[2]
    schedule_info['event'] = race_info.split(',')[3]
    schedule_info['date'] = race_info.split(':')[0].split(' ', 1)[0]
    schedule_info['meet_name'] = race_info.split(':')[0]
    schedule_info['distance'] = race_info.split(':')[1].split(' ')[1][:-1]
    schedule_info['race_style'] = race_info.split(':')[1].split(',')[
        0].split(' ', 2)[2]
    return schedule_info


def get_heat_schedule(lines: list) -> list:  # Checked
    heat = []
    heats = []
    for line in lines:
        if '#' not in line:
            heat.append(line)
        else:
            heats.append(heat)
            heat = []
    return heats

def update_meet_skater(meet_ID: int, skater_ID: int, engine: Engine) -> None:
    exist_check = (
        f'select exists'
        f'(select 1 '
        f'from "Meet_Skater" '
        f'where "meet_ID" = \'{meet_ID}\' '
        f'and "skater_ID" = \'{skater_ID}\');'
    )
    if not engine.execute(exist_check).fetchall()[0][0]:
        gender_age_qry = (
            f'select dob, "gender_ID" '
            f'from "Skater" '
            f'where "skater_ID" = {skater_ID};'
        )
        gender_age = pd.read_sql_query(gender_age_qry, engine)
        gender_ID = gender_age.iloc[0]['gender_ID']
        age = find_skating_age(gender_age.iloc[0]['dob'])
        division_ID = find_division(age, engine)
        qry = (
            f'insert into "Meet_Skater"("meet_ID", "skater_ID", "division_ID", "gender_ID") '
            f'values ({meet_ID}, {skater_ID}, {division_ID}, {gender_ID})'
        )
        engine.execute(qry)

def find_division(age:int, engine: Engine) -> int:
    qry = (
        f'select "division_ID" '
        f'from "Division" '
        f'where min_age <= {age} '
        f'and max_age >= {age};'
    )
    division = pd.read_sql_query(qry, engine)
    return division.iloc[0]['division_ID']


def get_lookup_df(table_name: str, engine: Engine) -> pd.DataFrame:
    return  pd.read_sql_query(f'select * from "{table_name}";', con=engine)

def create_race_division_result(meet_ID: int, event: int, engine: Engine) -> None:  # Checked
    # lookup_tables =  [ 'Race', 'Gender', 'Division', 'Meet']
    # for table in lookup_tables:
    #     f'table.lower() = 
    division_genders_race_qry = (
        f'select distinct rhrd."division_ID", rhrd."gender_ID", rhs."race_ID" '
        f'from "Race_Heat_Schedule" as rhs '
        f'left join "Race_Heat_Result" as rhr '
        f'on rhs."rhs_ID" = rhr."rhs_ID" '
        f'left join "Race_Heat_Result_Detail" as rhrd '
        f'on rhr."rhr_ID" = rhrd."rhr_ID" '
        f'where "meet_ID" = {meet_ID} and event = {event} '
        f'order by rhrd."division_ID";'
    )
    division_genders_race = pd.read_sql_query(division_genders_race_qry, engine)
    race = pd.read_sql_query('select * from "Race";', con=engine)
    gender = pd.read_sql_query('select * from "Gender";', con=engine)
    division = pd.read_sql_query('select * from "Division";', con=engine)
    meet = pd.read_sql_query('select * from "Meet";', con=engine)
    for idx, row in division_genders_race.iterrows():
        division_ID = row['division_ID']
        gender_ID = row['gender_ID']
        race_ID = row['race_ID']
        #print(meet_ID, division_ID, gender_ID, race_ID)
        exist_check = (
            f'select exists'
            f'(select 1 '
            f'from "Race_Division_Result" '
            f'where "division_ID" = {division_ID} '
            f'and "meet_ID" = {meet_ID} '
            f'and "gender_ID" = {gender_ID} '
            f'and "race_ID" = {race_ID});'
        )
        if not engine.execute(exist_check).fetchall()[0][0]:
            name = (
                f"{meet[meet['meet_ID']==meet_ID].iloc[0]['name']} "
                f"{gender[gender['gender_ID'] == gender_ID].iloc[0]['name']} "
                f"{division[division['division_ID']==division_ID].iloc[0]['name']} "
                f"{race[race['race_ID']==race_ID].iloc[0]['name']}"
            )
            qry = (
                f'insert into "Race_Division_Result"("division_ID", "meet_ID", "race_ID", "gender_ID", name) '
                f'values ({division_ID}, {meet_ID}, {race_ID}, {gender_ID}, \'{name}\')'
            )
            engine.execute(qry)
  
# Checked
def create_race_heat_schedule_and_detail(race_heat_schedules: dict, engine: Engine) -> None:
    race_style = pd.read_sql_query('select * from "Race_Style";', con=engine)
    skater = pd.read_sql_query('select * from "Skater";', con=engine)
    meet = pd.read_sql_query('select * from "Meet";', con=engine)
    race = pd.read_sql_query('select * from "Race";', con=engine)
    lane = pd.read_sql_query('select * from "Lane";', con=engine)
    heat = pd.read_sql_query('select * from "Heat";', con=engine)
    # division = pd.read_sql_query('select * from "Division";', con=engine)
    for race_schedule in race_heat_schedules.keys():
        each_heat = race_heat_schedules[race_schedule]
        # Construct race_heat_schedule first: race_ID / heat_ID / meet_ID / heat name / total skaters / bool team race
        total_skaters = len(each_heat['skaters'])
        distance = int(each_heat['heat_info']['distance'])
        event = int(each_heat['heat_info']['event'])
        race_type = each_heat['heat_info']['race_style']
        rs_ID = race_style[race_style['name'] == race_type].iloc[0]['rs_ID']
        race_ID = (race[(race['distance'] == distance) & (
            race['rs_ID'] == int(rs_ID))].iloc[0]['race_ID'])
        team_bool = race[race['race_ID'] == race_ID].iloc[0]['team']
        race_name = (race[(race['distance'] == distance) & (
            race['rs_ID'] == int(rs_ID))].iloc[0]['name'])
        meet_name = each_heat['heat_info']['meet_name']
        meet_ID = meet[meet['name'] == meet_name].iloc[0]['meet_ID']
        heat_ID = heat[heat['name'] ==
                       f"Heat {each_heat['heat_info']['heat']}"].iloc[0]['heat_ID']
        heat_name = f"{meet_name}: {race_name} Heat {each_heat['heat_info']['heat']}"
        # Check if heat_name exist
        exist_check = (
            f'select exists'
            f'(select 1 '
            f'from "Race_Heat_Schedule" '
            f'where name = \'{heat_name}\');'
        )
        if not engine.execute(exist_check).fetchall()[0][0]:
            qry = (
                f'insert into "Race_Heat_Schedule"("race_ID", "heat_ID", "meet_ID", event, name, total_skaters, team_race) '
                f'values ({race_ID}, {heat_ID}, {meet_ID}, {event}, \'{heat_name}\', {total_skaters}, {team_bool})'
            )
            engine.execute(qry)
        rhs_ID = engine.execute(
            f'select "rhs_ID" from "Race_Heat_Schedule" where name = \'{heat_name}\';').fetchall()[0][0]
        # print(rhs_ID)
        for heat_skater in each_heat['skaters']:
            # Create Race_Heat_Schedule_Detail
            if not team_bool:
                st_ID = 'null'
            skater_ID = skater[skater['club_member_number'] == int(
                heat_skater['skater_num'])].iloc[0]['skater_ID']
            lane_ID = lane[lane['name'] ==
                           heat_skater['lane_num']].iloc[0]['lane_ID']
            exist_check = (
                f'select exists'
                f'(select 1 '
                f'from "Race_Heat_Schedule_Detail" '
                f'where "rhs_ID" = \'{rhs_ID}\' '
                f'and "skater_ID" = \'{skater_ID}\');'
            )
            if not engine.execute(exist_check).fetchall()[0][0]:
                qry = (
                    f'insert into "Race_Heat_Schedule_Detail"("rhs_ID", "st_ID", "skater_ID", "lane_ID") '
                    f'values ({rhs_ID}, {st_ID}, {skater_ID}, {lane_ID})'
                )
                engine.execute(qry)
            update_meet_skater(meet_ID, skater_ID, engine)
            

def import_schedule(schedule_path: str) -> dict:  # Checked
    race_heat_schedules = {}
    with open(schedule_path, 'r') as schedules:
        lines = schedules.readlines()
    heats = get_heat_schedule(lines)
    for idx, heat in enumerate(heats, start=1):
        race_info = heat.pop(0)
        heat_info = find_schedule_info(race_info)
        heat_skaters = []
        for skater in heat:
            skater_info = {}
            skater = skater.split(',')
            skater_info['skater_num'] = skater[0]
            skater_info['lane_num'] = skater[1]
            skater_info['first_name'] = skater[2]
            skater_info['last_name'] = skater[3]
            skater_info['club'] = skater[4][:-1]
            heat_skaters.append(skater_info)
        race_heat_schedules[f'race{idx}'] = {
            'heat_info': heat_info, 'skaters': heat_skaters}
    return race_heat_schedules
    #create_race_heat_schedule_detail(race_heat_schedules, engine)


def create_race_heat_result(result_file: str, engine: Engine) -> dict:  # Checked
    race_heat_schedule = pd.read_sql_query(
        'select * from "Race_Heat_Schedule";', con=engine)
    with open(result_file, 'r') as result_file:
        lines = result_file.readlines()
    race_heat_schedule_name = f"{lines[0][:-1]} {lines[1].split(',')[0]}"
    rhs_ID = race_heat_schedule[race_heat_schedule['name']== race_heat_schedule_name].iloc[0]['rhs_ID']
    timestamp = lines[1].split('  ')[1][:-1]  # Remove \n from the line"
    if 'MT' in timestamp:
        timestamp = '00:00:00 AM'
        time_type = 'manual'
    else:
        time_type = 'automatic'
    timestamp = pd.to_datetime(timestamp).strftime('%H:%M:%S')
    exist_check = (
        f'select exists'
        f'(select 1 '
        f'from "Race_Heat_Result" '
        f'where "rhs_ID" = \'{rhs_ID}\');'
    )
    if not engine.execute(exist_check).fetchall()[0][0]:
        qry = (
            f'insert into "Race_Heat_Result"("rhs_ID", race_timestamp) '
            f'values ({rhs_ID}, \'{timestamp}\')'
        )
        engine.execute(qry)
    rhr_ID_qry = (
        f'select "rhr_ID" '
        f'from "Race_Heat_Result" '
        f'where "rhs_ID" = \'{rhs_ID}\';'
    )
    rhr_ID = engine.execute(rhr_ID_qry).fetchall()[0][0]
    return {'rhs_ID': rhs_ID, 'rhr_ID': rhr_ID, 'time_type': time_type}


def create_race_heat_result_detail(result_file: str, rhs_rhr: dict, engine: Engine) -> None:  # Checked
    # rhs_ID = rhs_rhr['rhs_ID']
    rhr_ID = rhs_rhr['rhr_ID']
    time_type = rhs_rhr['time_type']

    skater = pd.read_sql_query('select * from "Skater";', con=engine)
    lane = pd.read_sql_query('select * from "Lane";', con=engine)
    division = pd.read_sql_query('select * from "Division";', con=engine)
    #rhr_ID = create_race_heat_result(result_file)
    COLUMN_NAME = ['rank', 'club_member_number',
                   'lane', 'name', 'team', 'time']
    result_data = pd.read_csv(result_file, skiprows=2,
                              names=COLUMN_NAME, index_col=None)
    for each_result in result_data.iterrows():
        rank = each_result[1]['rank']
        if rank == 'dnf':
            status_ID = 1
            rank = 9999
            time = timedelta(seconds=9999)
            time_in_seconds = 9999
        else:
            status_ID = 2
            time_in_seconds = each_result[1]['time']
            time = timedelta(seconds=time_in_seconds)
        st_ID = None
        club_member_number = each_result[1]['club_member_number']
        lane_name = each_result[1]['lane'][1:]
        lane_ID = lane[lane['name'] == lane_name].iloc[0]['lane_ID']
        skater_ID = skater[skater['club_member_number']
                           == club_member_number].iloc[0]['skater_ID']
        gender_ID = skater[skater['skater_ID']
                           == skater_ID].iloc[0]['gender_ID']
        age = find_skating_age(
            skater[skater['skater_ID'] == skater_ID].iloc[0]['dob'])
        division_ID = division[(division['min_age'] <= age) & (
            division['max_age'] >= age)].iloc[0]['division_ID']
        exist_check = (
            f'select exists'
            f'(select 1 '
            f'from "Race_Heat_Result_Detail" '
            f'where "rhr_ID" = \'{rhr_ID}\' '
            f'and "skater_ID" = \'{skater_ID}\');'
        )
        if not engine.execute(exist_check).fetchall()[0][0]:
            qry = (
                f'insert into "Race_Heat_Result_Detail"'
                f'("rhr_ID", "skater_ID", "lane_ID", "status_ID", "division_ID", '
                f'"gender_ID", time_type, time, time_in_seconds, rank) '
                f'values ({rhr_ID}, {skater_ID}, {lane_ID}, {status_ID}, {division_ID}, '
                f'{gender_ID}, \'{time_type}\', \'{time}\',{time_in_seconds}, {rank})'
            )
            engine.execute(qry)

# Checked
def create_race_division_result_detail(meet_ID: int, race_ID: int, engine: Engine) -> None:
    race_heat_schedule = pd.read_sql_query(
        'select * from "Race_Heat_Schedule";', con=engine)
    race_heat_result_detail = pd.read_sql_query(
        'select * from "Race_Heat_Result_Detail";', con=engine)
    race_heat_result = pd.read_sql_query(
        'select * from "Race_Heat_Result";', con=engine)
    rhs_ID_list = (race_heat_schedule[(race_heat_schedule['meet_ID'] == meet_ID)
                                      & (race_heat_schedule['race_ID'] == race_ID)]['rhs_ID'].tolist())
    race_division_result = pd.read_sql_query(
        'select * from "Race_Division_Result";', con=engine)
    for rhs_ID in rhs_ID_list:
        possible_rhr_ID = race_heat_result[race_heat_result['rhs_ID'] == rhs_ID]
        # print(possible_rhr_ID)
        if not possible_rhr_ID.empty:
            rhr_ID = possible_rhr_ID['rhr_ID'].tolist()[0]
            # print(rhr_ID)
            #division_gender =(race_division_result[(race_division_result['meet_ID']==1) & (race_division_result['race_ID']==5)])
            division_gender = race_heat_result_detail[race_heat_result_detail['rhr_ID'] == rhr_ID]
            #division_gender = division_gender.drop(columns=['st_ID','lane_ID', 'status_ID', 'rank', 'mt_ID', 'skater_ID', 'rhr_ID'])
            for idx, row in division_gender.iterrows():
                division_ID = row['division_ID']
                rhrd_ID = row['rhrd_ID']
                gender_ID = row['gender_ID']
                # print(row)
                time_in_seconds = row['time_in_seconds']
                # find rdr_ID using division, gender, race, meet ID
                rdr_ID = (race_division_result[(race_division_result['division_ID'] == division_ID)
                                               & (race_division_result['meet_ID'] == meet_ID)
                                               & (race_division_result['race_ID'] == race_ID)
                                               & (race_division_result['gender_ID'] == gender_ID)].iloc[0]['rdr_ID'])
                # print(row)
                exist_check = (
                    f'select exists'
                    f'(select 1 '
                    f'from "Race_Division_Result_Detail" '
                    f'where "rdr_ID" = \'{rdr_ID}\' '
                    f'and "rhrd_ID" = \'{rhrd_ID}\');'
                )
                if not engine.execute(exist_check).fetchall()[0][0]:
                    qry = (
                        f'insert into "Race_Division_Result_Detail"("rdr_ID", "rhrd_ID", time_in_seconds) '
                        f'values ({rdr_ID}, {rhrd_ID}, {time_in_seconds})'
                    )
                    engine.execute(qry)


def rank_race_division_result(meet_ID: int, event: int, engine: Engine) -> None: #checked
    score = pd.read_sql_query('select * from "Score";', con=engine)
    qry = (
        f'select rdrd."rdr_ID" '
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
    for idx, rdr in rdr_ID_df.iterrows(): #For all races taken place for divisions and genders, iterate and get race_division_result ID
        rdr_ID = rdr[0]
        rank_query = (
            f'select rdrd."rdrd_ID", rdrd."rdr_ID", rhrd."rhrd_ID", rhrd.time '
            f'from "Race_Division_Result_Detail" as rdrd '
            f'left join "Race_Heat_Result_Detail" as rhrd '
            f'on rhrd."rhrd_ID" = rdrd."rhrd_ID" '
            f'left join "Race_Heat_Result" as rhr '
            f'on rhr."rhr_ID" = rhrd."rhr_ID" '
            f'left join "Race_Heat_Schedule" as rhs '
            f'on rhs."rhs_ID" = rhr."rhs_ID" '
            f'where rhs."meet_ID" = {meet_ID} and rhs.event = {event} and rdrd."rdr_ID" = {rdr_ID};'
        )
        ranking = pd.read_sql_query(rank_query, engine)
        if not ranking.empty:
            ranking['rank'] = ranking['time'].rank()
            for idx, each_rank in ranking.iterrows():
                rdrd_ID = each_rank.iloc[0]
                skater_rank = int(each_rank.iloc[4])
                if skater_rank < 9:
                    rank_score = score[score['rank'] == skater_rank].iloc[0]['point'] #Assign point based on the skater's rank 
                else:
                    rank_score = 0 #score should be 0 if the skater didn't place within 8
                #Update Race_Division_Result_Detail record based on rdrd_ID with the skater's rank and points
                qry = f'update "Race_Division_Result_Detail" set rank = {skater_rank}, score = {rank_score} where "rdrd_ID" = {rdrd_ID}'
                #Update DB
                engine.execute(qry)


def create_meet_division_result(meet_ID: int, engine: Engine) -> None:
    division_genders_qry = (
        f'select distinct "division_ID", "gender_ID" '
        f'from "Meet_Skater" where "meet_ID" = {meet_ID};'
    )
    division_genders = pd.read_sql_query(division_genders_qry, con=engine)
    meet_name = pd.read_sql_query(f'select name from "Meet" where "meet_ID" = {meet_ID};', con=engine)
    for idx, row in division_genders.iterrows():
        division_ID, gender_ID = row[0], row[1]
        division_name = pd.read_sql_query(f'select name from "Division" where "division_ID" = {division_ID};', con=engine)
        gender_name = pd.read_sql_query(f'select name from "Gender" where "gender_ID" = {gender_ID};', con=engine)
        report_name = f"{meet_name.iloc[0]['name']} {gender_name.iloc[0]['name']} {division_name.iloc[0]['name']} Result"
        exist_check = (
            f'select exists'
            f'(select 1 '
            f'from "Meet_Division_Result" '
            f'where "meet_ID" = {meet_ID} and "division_ID" = {division_ID} and "gender_ID" = {gender_ID});'
        )
        if not engine.execute(exist_check).fetchall()[0][0]:
            qry = (
                f'insert into "Meet_Division_Result"("meet_ID", "division_ID", "gender_ID", name) '
                f"values ({meet_ID}, {division_ID}, {gender_ID}, '{report_name}')"
            )
            engine.execute(qry)

def create_meet_division_result_detail(meet_ID: int, engine: Engine) -> None:
    division_genders_qry = (
        f'select distinct "mdr_ID", "division_ID", "gender_ID" '
        f'from "Meet_Division_Result" '
        f'where "meet_ID" = {meet_ID};'
    )
    division_genders = pd.read_sql_query(division_genders_qry, con=engine)
    for idx, row in division_genders.iterrows():
        event_scores = {}
        mdr_ID, division_ID, gender_ID = row[0], row[1], row[2]
        #print(idx)
        #print(meet_ID, division_ID, gender_ID)
        races_qry = (
            f'select distinct "rdr_ID" '
            f'from "Race_Division_Result" '
            f'where "meet_ID" = {meet_ID} '
            f'and "division_ID" = {division_ID} '
            f'and "gender_ID" = {gender_ID};'
        )
        races = pd.read_sql_query(races_qry, con=engine)
        #print(races)
        for idx, each_race in races.iterrows():
            rdr_ID = each_race[0]
            records_qry = (
                f'select rhrd."skater_ID", rdrd."score" '
                f'from "Race_Division_Result_Detail" as rdrd '
                f'left join "Race_Heat_Result_Detail" as rhrd '
                f'on rdrd."rhrd_ID" = rhrd."rhrd_ID" '
                f'where "rdr_ID" = {rdr_ID};'
            )
            records = pd.read_sql_query(records_qry, engine)
            for idx, record in records.iterrows():
                skater_ID, score = record[0], record[1]
                if skater_ID in event_scores.keys():
                    event_scores[skater_ID] += score
                else:
                    event_scores[skater_ID] = score
        for skater_ID in event_scores.keys():
            #print(key, event_scores[key])
            exist_check = (
                f'select exists('
                f'select 1 from "Meet_Division_Result_Detail" where "mdr_ID" = {mdr_ID} and "skater_ID" = {skater_ID});'
            )
            if not engine.execute(exist_check).fetchall()[0][0]:
                qry = (
                    f'insert into "Meet_Division_Result_Detail"("mdr_ID", "skater_ID", total_score) '
                    f'values ({mdr_ID}, {skater_ID}, {event_scores[skater_ID]})'
                )
                engine.execute(qry)



def rank_meet_division_result(meet_ID: int, engine: Engine) -> None:
    mdr = pd.read_sql_query(f'select distinct "mdr_ID" from "Meet_Division_Result" where "meet_ID" = {meet_ID}', engine)
    for idx, each_mdr in mdr.iterrows():
        mdr_ID = each_mdr[0]
        ranking = pd.read_sql_query(f'select * from "Meet_Division_Result_Detail" where "mdr_ID" = {mdr_ID}', engine)
        if not ranking.empty:
            ranking['rank'] = ranking['total_score'].rank(ascending=False)
            for idx, each_rank in ranking.iterrows():
                mdrd_ID = int(each_rank[0])
                skater_rank = int(each_rank[4])
                qry = f'update "Meet_Division_Result_Detail" set rank = {skater_rank} where "mdrd_ID" = {mdrd_ID}'
                    #Update DB
                engine.execute(qry)



def update_club(club_file: str, engine: Engine) -> None:
    new_clubs = pd.read_csv(club_file)

    for idx, row in new_clubs.iterrows():
        abbreviation = row['abbreviation']
        exist_check = (
            f'select exists('
            f'select 1 from "Club" '
            f'where abbreviation = \'{abbreviation}\');'
        )
        if not engine.execute(exist_check).fetchall()[0][0]:
            qry = (
                f'insert into "Club"(us_based, name, abbreviation) '
                f'values ({row["us_based"]}, \'{row["name"]}\', \'{abbreviation}\')'
            )
            engine.execute(qry)
'''
skater: dict
keys = ['club_ID', 'gender_ID', 'clube_member_number', 'first_name', 'last_name', 'dob',
 'ngb_member_number, 'ngb_name']
'''
def update_skater(skater: dict, engine: Engine) -> None:
    exist_check = (
        f'select exists('
        f'select 1 from "Skater" '
        f'where club_member_number = {skater["club_member_number"]};'
    )
    if not engine.execute(exist_check).fetchall()[0][0]:
        qry = (
            f'insert into "Skater("club_ID", "gender_ID", club_member_number, first_name, last_name, dob, ngb_member_number, ngb_name) '
            f'values ({skater["club_ID"]}, {skater["gender_ID"]}, {skater["club_member_number"]}, \'{skater["first_name"]}\', '
            f'\'{skater["last_name"]}\', {skater["dob"]}, {skater["ngb_member_number"]}, \'{skater["ngb_name"]}\';',
        )
        engine.execute(qry)