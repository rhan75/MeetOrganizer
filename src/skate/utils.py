from sqlalchemy.engine.base import Engine
from sqlalchemy import select, exists, and_
from sqlalchemy.orm import sessionmaker, declarative_base, aliased
import pandas as pd
from datetime import timedelta, date 
from .model import *


def prep_session(engine: Engine) -> sessionmaker:
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

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
    schedule_info['competition_name'] = race_info.split(':')[0]
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

def update_competition_skater(competition_id: int, skater_id: int, engine: Engine) -> None:
    session = prep_session(engine=engine)
    if not session.query(exists().where(Competition_Skater.id == competition_id and Competition_Skater.skater_id == skater_id)):
        gender_age = session.query(Skater).filter(Skater.id == skater_id).with_entities(Skater.dob, Skater.gender_id).first()
        age = find_skating_age(gender_age.dob)
        age_group_id = find_division(age, engine)
        new_comp_skater = Competition_Skater(competition_id=competition_id, skater_id=skater_id, age_group_id=age_group_id, gender_id=gender_age.id)
        session.add(new_comp_skater)
        session.commit()


def find_division(age:int, engine: Engine) -> int:
    session = prep_session(engine=engine)
    age_group_info = session.query(Age_Group).filter(and_(Age_Group.min_age <= age, Age_Group.max_age >= age)).first()
    return age_group_info.id
    

def create_race_age_group_result(competition_id: int, event: int, engine: Engine) -> None:  # Checked
    # session = prep_session(engine=engine)
    # RHS = aliased(Race_Heat_Schedule)
    # RHR = aliased(Race_Heat_Result)
    # RHRD = aliased(Race_Heat_Result_Detail)
    # #Age_Group_Gender_Race
    # AGGR = session.query(RHS, RHR, RHRD).outerjoin(RHR, RHS.id == RHR.rhs_id)\
    #     .outerjoin(RHRD, RHR.id == RHRD.rhr_id)\
    #     .filter(RHS.competition_id == competition_id & RHS.event == event)\
    #     .distinct().with_entities(RHRD.ag_id, RHRD.gender_ID, RHS.race_id).order_by(RHRD.ag_id).all()


    # lookup_tables =  [ 'Race', 'Gender', 'Division', 'Meet']
    # for table in lookup_tables:
    #     f'table.lower() = 
    division_genders_race_qry = (
        f'select distinct rhrd.age_group_id, rhrd.gender_id, rhs.race_id '
        f'from race_heat_schedule as rhs '
        f'left join race_heat_result as rhr '
        f'on rhs.rhs_id = rhr.rhs_id '
        f'left join race_heat_result_detail as rhrd '
        f'on rhr.rhr_id = rhrd.rhr_id '
        f'where competition_id = {competition_id} and event = {event} '
        f'order by rhrd.age_group_id;'
    )
    division_genders_race = pd.read_sql_query(division_genders_race_qry, engine)
    race = pd.read_sql_query('select * from race;', con=engine)
    gender = pd.read_sql_query('select * from gender;', con=engine)
    division = pd.read_sql_query('select * from age_group;', con=engine)
    meet = pd.read_sql_query('select * from competition;', con=engine)
    for idx, row in division_genders_race.iterrows():
        age_group_id = row['age_group_id']
        gender_id = row['gender_id']
        race_id = row['race_id']
        #print(competition_id, age_group_id, gender_id, race_id)
        exist_check = (
            f'select exists'
            f'(select 1 '
            f'from race_age_group_result '
            f'where age_group_id = {age_group_id} '
            f'and competition_id = {competition_id} '
            f'and gender_id = {gender_id} '
            f'and race_id = {race_id});'
        )
        if not engine.execute(exist_check).fetchall()[0][0]:
            name = (
                f"{meet[meet['competition_id']==competition_id].iloc[0]['name']} "
                f"{gender[gender['gender_id'] == gender_id].iloc[0]['name']} "
                f"{division[division['age_group_id']==age_group_id].iloc[0]['name']} "
                f"{race[race['race_id']==race_id].iloc[0]['name']}"
            )
            qry = (
                f'insert into race_age_group_result(age_group_id, competition_id, race_id, gender_id, name) '
                f'values ({age_group_id}, {competition_id}, {race_id}, {gender_id}, \'{name}\')'
            )
            engine.execute(qry)
  
# Checked
def create_race_heat_schedule_and_detail(race_heat_schedules: dict, engine: Engine) -> None:
    session = prep_session(engine=engine)
    RHS = aliased(Race_Heat_Schedule)
    RHSD = aliased(Race_Heat_Schedule_Detail)
    RHRD = aliased(Race_Heat_Result_Detail)
    
    for race_schedule in race_heat_schedules.keys():
        each_heat = race_heat_schedules[race_schedule]
        # Construct race_heat_schedule first: race_id / heat_id / competition_id / heat name / total skaters / bool team race
        total_skaters = len(each_heat['skaters'])
        distance = int(each_heat['heat_info']['distance'])
        event = int(each_heat['heat_info']['event'])
        race_type = each_heat['heat_info']['race_style']
        rs_id = session.query(Race_Style).filter(Race_Style.name == race_type).with_entities(Race_Style.id).first()[0]
        # rs_id = race_style[race_style['name'] == race_type].iloc[0]['rs_id']
        current_race = session.query(Race).filter(and_(Race.distance == distance, Race.rs_id == rs_id)).first()
        race_id = current_race.id
        team_bool = current_race.team
        competition_name = each_heat['heat_info']['competition_name']
        current_competition = session.query(Competition).filter(Competition.name == competition_name).first()
        competition_id = current_competition.id
        # competition_id = meet[meet['name'] == competition_name].iloc[0]['competition_id']
        current_heat = session.query(Heat).filter(Heat.name == f"Heat {each_heat['heat_info']['heat']}").first()
        heat_id = current_heat.id
        heat_name = current_heat.name
        if not session.query(exists().where(Heat.name == heat_name)):
            new_heat_schedule = RHS(race_id=race_id, heat_id=heat_id, competition_id = competition_id, event=event, heat_name=heat_name, total_skaters=total_skaters, team_race=team_bool)
            session.add(new_heat_schedule)
            session.commit()
        current_race_heat_schedule = session.query(RHS).filter(RHS.name == heat_name).first()
        race_heat_schedules_id = current_race_heat_schedule.id
        for heat_skater in each_heat['skaters']:
            # Create Race_Heat_Schedule_Detail
            if not team_bool:
                st_id = 'null'
            current_skater = session.query(Skater).filter(Skater.club_member_number == heat_skater['skater_num']).first()
            skater_id = current_skater.id
            current_lane = session.query(Lane).filter(Lane.name == heat_skater['lane_num']).first()
            lane_id = current_lane.id
            if not session.query(exists(RHSD).where(RHSD.skater_id == skater_id & RHSD.race_heat_schedule_id == race_heat_schedules_id)):
                new_rhsd_record = RHRD(race_heat_schedules_id=race_heat_schedules_id, st_id=st_id, skater_id=skater_id, lane_id=lane_id)
                session.add(new_rhsd_record)
                session.commit()
            update_competition_skater(competition_id, skater_id, engine)
            

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
        'select * from race_heat_schedule;', con=engine)
    with open(result_file, 'r') as result_file:
        lines = result_file.readlines()
    race_heat_schedule_name = f"{lines[0][:-1]} {lines[1].split(',')[0]}"
    rhs_id = race_heat_schedule[race_heat_schedule['name']== race_heat_schedule_name].iloc[0]['rhs_id']
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
        f'from race_heat_result '
        f'where rhs_id = \'{rhs_id}\');'
    )
    if not engine.execute(exist_check).fetchall()[0][0]:
        qry = (
            f'insert into race_heat_result(rhs_id, race_timestamp) '
            f'values ({rhs_id}, \'{timestamp}\')'
        )
        engine.execute(qry)
    rhr_id_qry = (
        f'select rhr_id '
        f'from race_heat_result '
        f'where rhs_id = \'{rhs_id}\';'
    )
    rhr_id = engine.execute(rhr_id_qry).fetchall()[0][0]
    return {'rhs_id': rhs_id, 'rhr_id': rhr_id, 'time_type': time_type}


def create_race_heat_result_detail(result_file: str, rhs_rhr: dict, engine: Engine) -> None:  # Checked
    # rhs_id = rhs_rhr['rhs_id']
    rhr_id = rhs_rhr['rhr_id']
    time_type = rhs_rhr['time_type']

    skater = pd.read_sql_query('select * from skater;', con=engine)
    lane = pd.read_sql_query('select * from lane;', con=engine)
    division = pd.read_sql_query('select * from age_group;', con=engine)
    #rhr_id = create_race_heat_result(result_file)
    COLUMN_NAME = ['rank', 'club_member_number',
                   'lane', 'name', 'team', 'time']
    result_data = pd.read_csv(result_file, skiprows=2,
                              names=COLUMN_NAME, index_col=None)
    for each_result in result_data.iterrows():
        rank = each_result[1]['rank']
        if rank == 'dnf':
            status_id = 1
            rank = 9999
            time = timedelta(seconds=9999)
            time_in_seconds = 9999
        else:
            status_id = 2
            time_in_seconds = each_result[1]['time']
            time = timedelta(seconds=time_in_seconds)
        st_id = None
        club_member_number = each_result[1]['club_member_number']
        lane_name = each_result[1]['lane'][1:]
        lane_id = lane[lane['name'] == lane_name].iloc[0]['lane_id']
        skater_id = skater[skater['club_member_number']
                           == club_member_number].iloc[0]['skater_id']
        gender_id = skater[skater['skater_id']
                           == skater_id].iloc[0]['gender_id']
        age = find_skating_age(
            skater[skater['skater_id'] == skater_id].iloc[0]['dob'])
        age_group_id = division[(division['min_age'] <= age) & (
            division['max_age'] >= age)].iloc[0]['age_group_id']
        exist_check = (
            f'select exists'
            f'(select 1 '
            f'from race_heat_result_detail '
            f'where rhr_id = \'{rhr_id}\' '
            f'and skater_id = \'{skater_id}\');'
        )
        if not engine.execute(exist_check).fetchall()[0][0]:
            qry = (
                f'insert into race_heat_result_detail'
                f'(rhr_id, skater_id, lane_id, status_id, age_group_id, '
                f'gender_id, time_type, time, time_in_seconds, rank) '
                f'values ({rhr_id}, {skater_id}, {lane_id}, {status_id}, {age_group_id}, '
                f'{gender_id}, \'{time_type}\', \'{time}\',{time_in_seconds}, {rank})'
            )
            engine.execute(qry)

# Checked
def create_race_age_group_result_detail(competition_id: int, race_id: int, engine: Engine) -> None:
    race_heat_schedule = pd.read_sql_query(
        'select * from race_heat_schedule;', con=engine)
    race_heat_result_detail = pd.read_sql_query(
        'select * from race_heat_result_detail;', con=engine)
    race_heat_result = pd.read_sql_query(
        'select * from race_heat_result;', con=engine)
    rhs_id_list = (race_heat_schedule[(race_heat_schedule['competition_id'] == competition_id)
                                      & (race_heat_schedule['race_id'] == race_id)]['rhs_id'].tolist())
    race_age_group_result = pd.read_sql_query(
        'select * from race_age_group_result;', con=engine)
    for rhs_id in rhs_id_list:
        possible_rhr_id = race_heat_result[race_heat_result['rhs_id'] == rhs_id]
        # print(possible_rhr_id)
        if not possible_rhr_id.empty:
            rhr_id = possible_rhr_id['rhr_id'].tolist()[0]
            # print(rhr_id)
            #division_gender =(race_age_group_result[(race_age_group_result['competition_id']==1) & (race_age_group_result['race_id']==5)])
            division_gender = race_heat_result_detail[race_heat_result_detail['rhr_id'] == rhr_id]
            #division_gender = division_gender.drop(columns=['st_id','lane_id', 'status_id', 'rank', 'mt_id', 'skater_id', 'rhr_id'])
            for idx, row in division_gender.iterrows():
                age_group_id = row['age_group_id']
                race_heat_result_detail_id = row['race_heat_result_detail_id']
                gender_id = row['gender_id']
                # print(row)
                time_in_seconds = row['time_in_seconds']
                # find race_age_group_result_id using division, gender, race, meet ID
                race_age_group_result_id = (race_age_group_result[(race_age_group_result['age_group_id'] == age_group_id)
                                               & (race_age_group_result['competition_id'] == competition_id)
                                               & (race_age_group_result['race_id'] == race_id)
                                               & (race_age_group_result['gender_id'] == gender_id)].iloc[0]['race_age_group_result_id'])
                # print(row)
                exist_check = (
                    f'select exists'
                    f'(select 1 '
                    f'from race_age_group_result_detail '
                    f'where race_age_group_result_id = \'{race_age_group_result_id}\' '
                    f'and rhrd_id = \'{race_heat_result_detail_id}\');'
                )
                if not engine.execute(exist_check).fetchall()[0][0]:
                    qry = (
                        f'insert into race_age_group_result_detail(race_age_group_result_id, rhrd_id, time_in_seconds) '
                        f'values ({race_age_group_result_id}, {race_heat_result_detail_id}, {time_in_seconds})'
                    )
                    engine.execute(qry)


def rank_race_age_group_result(competition_id: int, event: int, engine: Engine) -> None: #checked
    score = pd.read_sql_query('select * from score;', con=engine)
    qry = (
        f'select rdrd.race_age_group_result_id '
        f'from race_heat_result as rhr '
        f'left join race_heat_schedule as rhs '
        f'on rhs.id = rhr.rhs_id '
        f'left join race_heat_result_detail as rhrd '
        f'on rhrd.rhr_id = rhr.id '
        f'left join race_age_group_result_detail as rdrd '
        f'on rdrd.rhrd_id = rhrd.rhrd_id '
        f'where rhs.competition_id = {competition_id} and rhs.event = {event};'
    )
    race_age_group_result_id_df = pd.read_sql_query(qry, engine)
    for idx, rdr in race_age_group_result_id_df.iterrows(): #For all races taken place for divisions and genders, iterate and get race_age_group_result ID
        race_age_group_result_id = rdr[0]
        rank_query = (
            f'select rdrd.race_age_group_result_detail_id, rdrd.race_age_group_result_id, rhrd.rhrd_id, rhrd.time '
            f'from race_age_group_result_detail as rdrd '
            f'left join race_heat_result_detail as rhrd '
            f'on rhrd.rhrd_id = rdrd.rhrd_id '
            f'left join race_heat_result as rhr '
            f'on rhr.rhr_id = rhrd.rhr_id '
            f'left join race_heat_schedule as rhs '
            f'on rhs.rhs_id = rhr.rhs_id '
            f'where rhs.competition_id = {competition_id} and rhs.event = {event} and rdrd.race_age_group_result_id = {race_age_group_result_id};'
        )
        ranking = pd.read_sql_query(rank_query, engine)
        if not ranking.empty:
            ranking['rank'] = ranking['time'].rank()
            for idx, each_rank in ranking.iterrows():
                rdrd_id = each_rank.iloc[0]
                skater_rank = int(each_rank.iloc[4])
                if skater_rank < 9:
                    rank_score = score[score['rank'] == skater_rank].iloc[0]['point'] #Assign point based on the skater's rank 
                else:
                    rank_score = 0 #score should be 0 if the skater didn't place within 8
                #Update Race_Division_Result_Detail record based on rdrd_id with the skater's rank and points
                qry = f'update race_age_group_result_detail set rank = {skater_rank}, score = {rank_score} where race_age_group_result_detail_id = {rdrd_id}'
                #Update DB
                engine.execute(qry)


def create_competition_age_group_result(competition_id: int, engine: Engine) -> None:
    division_genders_qry = (
        f'select distinct age_group_id, gender_id '
        f'from competition_skater where competition_id = {competition_id};'
    )
    division_genders = pd.read_sql_query(division_genders_qry, con=engine)
    competition_name = pd.read_sql_query(f'select name from competition where competition_id = {competition_id};', con=engine)
    for idx, row in division_genders.iterrows():
        age_group_id, gender_id = row[0], row[1]
        division_name = pd.read_sql_query(f'select name from age_group where age_group_id = {age_group_id};', con=engine)
        gender_name = pd.read_sql_query(f'select name from gender where gender_id = {gender_id};', con=engine)
        report_name = f"{competition_name.iloc[0]['name']} {gender_name.iloc[0]['name']} {division_name.iloc[0]['name']} Result"
        exist_check = (
            f'select exists'
            f'(select 1 '
            f'from competition_age_group_result '
            f'where competition_id = {competition_id} and age_group_id = {age_group_id} and gender_id = {gender_id});'
        )
        if not engine.execute(exist_check).fetchall()[0][0]:
            qry = (
                f'insert into competition_age_group_result(competition_id, age_group_id, gender_id, name) '
                f"values ({competition_id}, {age_group_id}, {gender_id}, '{report_name}')"
            )
            engine.execute(qry)

def create_competition_age_group_result_detail(competition_id: int, engine: Engine) -> None:
    division_genders_qry = (
        f'select distinct competition_age_group_result_id, age_group_id, gender_id '
        f'from competition_age_group_result '
        f'where competition_id = {competition_id};'
    )
    division_genders = pd.read_sql_query(division_genders_qry, con=engine)
    for idx, row in division_genders.iterrows():
        event_scores = {}
        mdr_id, age_group_id, gender_id = row[0], row[1], row[2]
        #print(idx)
        #print(competition_id, age_group_id, gender_id)
        races_qry = (
            f'select distinct race_age_group_result_id '
            f'from race_age_group_result '
            f'where competition_id = {competition_id} '
            f'and age_group_id = {age_group_id} '
            f'and gender_id = {gender_id};'
        )
        races = pd.read_sql_query(races_qry, con=engine)
        #print(races)
        for idx, each_race in races.iterrows():
            race_age_group_result_id = each_race[0]
            records_qry = (
                f'select rhrd.skater_id, rdrd.score '
                f'from race_age_group_result_detail as rdrd '
                f'left join race_heat_result_detail as rhrd '
                f'on rdrd.race_heat_result_detail_id = rhrd.id '
                f'where race_age_group_result_id = {race_age_group_result_id};'
            )
            records = pd.read_sql_query(records_qry, engine)
            for idx, record in records.iterrows():
                skater_id, score = record[0], record[1]
                if skater_id in event_scores.keys():
                    event_scores[skater_id] += score
                else:
                    event_scores[skater_id] = score
        for skater_id in event_scores.keys():
            #print(key, event_scores[key])
            exist_check = (
                f'select exists('
                f'select 1 from competition_age_group_result_detail where competition_age_group_result_id = {mdr_id} and skater_id = {skater_id});'
            )
            if not engine.execute(exist_check).fetchall()[0][0]:
                qry = (
                    f'insert into competition_age_group_result_detail(competition_age_group_result_id, skater_id, total_score) '
                    f'values ({mdr_id}, {skater_id}, {event_scores[skater_id]})'
                )
                engine.execute(qry)



def rank_competition_age_group_result(competition_id: int, engine: Engine) -> None:
    mdr = pd.read_sql_query(f'select distinct competition_age_group_result_id from competition_age_group_result where competition_id = {competition_id}', engine)
    for idx, each_mdr in mdr.iterrows():
        mdr_id = each_mdr[0]
        ranking = pd.read_sql_query(f'select * from competition_age_group_result_detail where competition_age_group_result_id = {mdr_id}', engine)
        if not ranking.empty:
            ranking['rank'] = ranking['total_score'].rank(ascending=False)
            for idx, each_rank in ranking.iterrows():
                mdrd_id = int(each_rank[0])
                skater_rank = int(each_rank[4])
                qry = f'update competition_age_group_result_detail set rank = {skater_rank} where competition_age_group_result_detail_id = {mdrd_id}'
                    #Update DB
                engine.execute(qry)



def update_club(club_file: str, engine: Engine) -> None:
    new_clubs = pd.read_csv(club_file)

    for idx, row in new_clubs.iterrows():
        abbreviation = row['abbreviation']
        exist_check = (
            f'select exists('
            f'select 1 from club '
            f'where abbreviation = \'{abbreviation}\');'
        )
        if not engine.execute(exist_check).fetchall()[0][0]:
            qry = (
                f'insert into club(us_based, name, abbreviation) '
                f'values ({row["us_based"]}, \'{row["name"]}\', \'{abbreviation}\')'
            )
            engine.execute(qry)
'''
skater: dict
keys = ['club_id', 'gender_id', 'clube_member_number', 'first_name', 'last_name', 'dob',
 'ngb_member_number, 'ngb_name']
'''
def update_skater(skater: dict, engine: Engine) -> None:
    exist_check = (
        f'select exists('
        f'select 1 from skater '
        f'where club_member_number = {skater["club_member_number"]};'
    )
    if not engine.execute(exist_check).fetchall()[0][0]:
        qry = (
            f'insert into skater(club_id, gender_id, club_member_number, first_name, last_name, dob, ngb_member_number, ngb_name) '
            f'values ({skater["club_id"]}, {skater["gender_id"]}, {skater["club_member_number"]}, \'{skater["first_name"]}\', '
            f'\'{skater["last_name"]}\', {skater["dob"]}, {skater["ngb_member_number"]}, \'{skater["ngb_name"]}\';',
        )
        engine.execute(qry)