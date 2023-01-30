from sqlalchemy.engine.base import Engine
from sqlalchemy import exists, and_
from sqlalchemy.orm import sessionmaker, aliased
import pandas as pd
from datetime import timedelta, date, datetime
from .model import *

# Aliases for DB Tables ORM
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

    if not session.query(exists().where(and_(Competition_Skater.id == competition_id, Competition_Skater.skater_id == skater_id))).scalar():
        gender_age = session.query(Skater).filter(Skater.id == skater_id).with_entities(Skater.dob, Skater.gender_id).first()
        age = find_skating_age(gender_age.dob)
        ag_id = find_division(age, engine)
        new_comp_skater = Competition_Skater(competition_id=competition_id, skater_id=skater_id, ag_id=ag_id, gender_id=gender_age.gender_id)
        session.add(new_comp_skater)
        session.commit()
    session.close()


def find_division(age:int, engine: Engine) -> int:
    session = prep_session(engine=engine)
    age_group_info = session.query(Age_Group).filter(and_(Age_Group.min_age <= age, Age_Group.max_age >= age)).first()
    session.close()
    return age_group_info.id
    

def create_race_age_group_result(competition_id: int, event: int, engine: Engine) -> None:  # Checked
    session = prep_session(engine=engine)
    # competition_id = (competition_id)
    # event = int(event)
    print(competition_id, event)

    #Age_Group_Gender_Race
    AGGR = session.query(RHS.race_id, RHRD.ag_id, RHRD.gender_id).outerjoin(RHR, RHS.id == RHR.rhs_id)\
        .outerjoin(RHRD, RHR.id == RHRD.rhr_id).where(and_(RHS.competition_id == competition_id, RHS.event == event))\
        .distinct().order_by(RHRD.ag_id).all()

    race = session.query(Race)
    gender = session.query(Gender)
    age_group = session.query(Age_Group)
    competition = session.query(Competition)

    for row in AGGR:
        ag_id = row.ag_id
        gender_id = row.gender_id
        race_id = row.race_id
        print(ag_id, gender_id, race_id)
        if not session.query(exists().where(and_(RAGR.ag_id == ag_id, RAGR.competition_id == competition_id, RAGR.gender_id == gender_id, RAGR.event == event))).scalar():
            name = (
                f"{competition.where(Competition.id == competition_id).first().name} "
                f"{gender.where(Gender.id == gender_id).first().name} "
                f"{age_group.where(Age_Group.id == ag_id).first().name} "
                f"{race.where(Race.id == race_id).first().name}"
            )
            new_ragr = Race_Age_Group_Result(ag_id=ag_id, competition_id=competition_id, race_id=race_id, gender_id=gender_id, event=event, name=name)
            session.add(new_ragr)
            session.commit()
    session.close()

  
# Checked
def create_race_heat_schedule_and_detail(race_heat_schedules: dict, engine: Engine) -> None:
    session = prep_session(engine=engine)
    
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
        heat_name = f"{competition_name}: {current_race.name} Heat {each_heat['heat_info']['heat']}"
        #print(heat_name)
        #print(heat_id, heat_name, total_skaters, race_id, competition_id)
        if not session.query(exists().where(RHS.name == heat_name)).scalar():
            #print('creating new schedule')
            new_heat_schedule = Race_Heat_Schedule(race_id=race_id, heat_id=heat_id, competition_id = competition_id, event=event, name=heat_name, total_skaters=total_skaters, team_race=team_bool)
            session.add(new_heat_schedule)
            session.commit()
        
        current_race_heat_schedule = session.query(RHS).filter(RHS.name == heat_name).first()
        rhs_id = current_race_heat_schedule.id
        for heat_skater in each_heat['skaters']:
            # Create Race_Heat_Schedule_Detail
            #print(heat_skater)

            current_skater = session.query(Skater).filter(Skater.club_member_number == heat_skater['skater_num']).first()
            # if current_skater.empty:
            print(heat_skater['skater_num'])
            skater_id = current_skater.id
            current_lane = session.query(Lane).filter(Lane.name == heat_skater['lane_num']).first()
            lane_id = current_lane.id
            if not session.query(exists(RHSD).where(and_(RHSD.skater_id == skater_id, RHSD.rhs_id == rhs_id))).scalar():
                new_rhsd_record = Race_Heat_Schedule_Detail(rhs_id=rhs_id, skater_id=skater_id, lane_id=lane_id)
                session.add(new_rhsd_record)
                session.commit()
            update_competition_skater(competition_id, skater_id, engine)
    session.close()
            

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
    print(race_heat_schedules)
    return race_heat_schedules
    #create_race_heat_schedule_detail(race_heat_schedules, engine)


def create_race_heat_result(result_file: str, engine: Engine) -> dict:  # Checked
    session = prep_session(engine=engine)

    # race_heat_schedule = pd.read_sql_query(
    #     'select * from race_heat_schedule;', con=engine)
    with open(result_file, 'r') as result_file:
        lines = result_file.readlines()
    race_heat_schedule_name = f"{lines[0][:-1]} {lines[1].split(',')[0]}"
    print(race_heat_schedule_name)
    # rhs_id = race_heat_schedule[race_heat_schedule['name']== race_heat_schedule_name].iloc[0]['id']
    rhs_id = session.query(RHS).where(RHS.name == race_heat_schedule_name).first().id
    timestamp = lines[1].split('  ')[1][:-1]  # Remove \n from the line"
    if 'MT' in timestamp:
        timestamp = '00:00:00 AM'
        time_type = 'manual'
    else:
        time_type = 'automatic'
    timestamp = pd.to_datetime(timestamp).strftime('%H:%M:%S')
    if not session.query(exists().where(RHR.rhs_id == rhs_id)).scalar():
        #    session.query(exists()).where(RHR.rhs_id == rhs_id).scalar():
        new_rhr = Race_Heat_Result(rhs_id = rhs_id, timestamp = timestamp)
        session.add(new_rhr)
        session.commit()
    rhr_id = session.query(RHR).where(RHR.rhs_id == rhs_id).first().id
    # rhr_id = engine.execute(rhr_id_qry).fetchall()[0][0]
    session.close()
    return {'rhr_id': rhr_id, 'time_type': time_type}


def is_valid_time_in_second(time_string):
    try:
        time_format = '%S.%f'
        datetime.strptime(time_string, time_format)
        return True
    except ValueError:
        return False

def is_valid_time(time_string):
    try:
        time_format = '%M:%S.%f'
        datetime.strptime(time_string, time_format)
        return True
    except ValueError:
        return False

def create_race_heat_result_detail(result_file: str, rhs_rhr: dict, engine: Engine) -> None:  # Checked
    session = prep_session(engine=engine)

    rhr_id = rhs_rhr['rhr_id']
    time_type = rhs_rhr['time_type']

    COLUMN_NAME = ['rank', 'club_member_number',
                   'lane', 'name', 'team', 'time']
    datatype = {'rank':str, 'club_member_number': int, 'lane': str, 'name': str, 'team': str, 'time': str}
    result_data = pd.read_csv(result_file, skiprows=2, dtype=datatype, names=COLUMN_NAME, index_col=None)
    for each_result in result_data.iterrows():
        rank = each_result[1]['rank']
        if rank == 'dnf':
            status_id = 1
        else:
            rank = int(rank)
            status_id = 2
            time_in_seconds = each_result[1]['time']
            if is_valid_time(time_in_seconds):
                time_format = '%M:%S.%f'
                time_datetime = datetime.strptime(time_in_seconds, time_format)
                time_in_seconds = (time_datetime.minute *60) + time_datetime.second + (time_datetime.microsecond/1000000)
                
            else:
                time_in_seconds = float(time_in_seconds)
            time_value = timedelta(seconds=time_in_seconds)
            # time_value = time_value.replace

        st_id = None
        club_member_number = each_result[1]['club_member_number']
        lane_name = each_result[1]['lane'][1:]
        lane_id = session.query(Lane).where(Lane.name == lane_name).first().id
        skater_id = session.query(Skater).where(Skater.club_member_number == club_member_number).first().id
        gender_id = session.query(Skater).where(Skater.id == skater_id).first().gender_id
        age = find_skating_age(session.query(Skater).where(Skater.id == skater_id).first().dob)
        ag_id = session.query(Age_Group).where(and_(Age_Group.min_age <= age, Age_Group.max_age >= age)).first().id
  
        if not session.query(exists().where(and_(RHRD.rhr_id == rhr_id, RHRD.skater_id == skater_id))).scalar():
            if status_id == 1:
                new_rhrd = Race_Heat_Result_Detail(rhr_id=rhr_id, skater_id=skater_id, lane_id=lane_id, status_id=status_id, ag_id=ag_id, \
                    gender_id=gender_id, time_type=time_type)
            else:
                new_rhrd = Race_Heat_Result_Detail(rhr_id=rhr_id, skater_id=skater_id, lane_id=lane_id, status_id=status_id, ag_id=ag_id, \
                    gender_id=gender_id, time_type=time_type, time=time_value, time_in_seconds=time_in_seconds, rank=rank)
            session.add(new_rhrd)
            session.commit()
    session.close()


# Checked
def create_race_age_group_result_detail(competition_id: int, event: int, race_id: int, engine: Engine) -> None:
    session = prep_session(engine=engine)
    rhs_ids = session.query(RHS.id).where(and_(RHS.competition_id == competition_id, RHS.race_id == race_id, RHS.event == event)).all()
    rhs_id_list = [rhs_id.id for rhs_id in rhs_ids]
    for rhs_id in rhs_id_list:
        rhr_id = session.query(RHR.id).where(RHR.rhs_id == rhs_id).first().id
        rhrd_results = session.query(RHRD).where(RHRD.rhr_id == rhr_id).all()
        for result in rhrd_results:
            ag_id, rhrd_id, gender_id, time_in_seconds = result.ag_id, result.id, result.gender_id, result.time_in_seconds
            print(ag_id, rhrd_id, gender_id, time_in_seconds, rhr_id, rhs_id, race_id)
            ragr_id = session.query(RAGR.id).where(and_(RAGR.event == event, RAGR.ag_id == ag_id, RAGR.competition_id == competition_id, RAGR.race_id == race_id, RAGR.gender_id == gender_id)).first().id
            if not session.query(exists().where(and_(RAGRD.ragr_id == ragr_id, RAGRD.rhrd_id==rhrd_id))).scalar():
                new_ragrd = Race_Age_Group_Result_Detail(ragr_id=ragr_id, rhrd_id=rhrd_id, time_in_seconds=time_in_seconds)
                session.add(new_ragrd)
                session.commit()
    session.close()

def rank_race_age_group_result(competition_id: int, event: int, engine: Engine) -> None: #checked
    session = prep_session(engine=engine)
    ragr_id_df = session.query(RHR, RHS, RHRD, RAGRD).outerjoin(RHS, RHS.id == RHR.rhs_id)\
        .outerjoin(RHRD,RHRD.rhr_id == RHR.id)\
        .outerjoin(RAGRD, RAGRD.rhrd_id == RHRD.id)\
        .filter(and_(RHS.competition_id == competition_id, RHS.event == event))\
        .distinct().with_entities(RAGRD.ragr_id).all()
    ragr_ids = [ragr_id[0] for ragr_id in ragr_id_df]
    ranking_col = ['ragrd_id', 'ragr_id', 'rhrd_id', 'time']
    for ragr_id in ragr_ids: #For all races taken place for divisions and genders, iterate and get race_age_group_result ID
        ranking = session.query(RAGRD.id, RAGRD.ragr_id, RHRD.id, RHRD.time).outerjoin(RHRD, RHRD.id==RAGRD.rhrd_id)\
            .outerjoin(RHR, RHR.id == RHRD.rhr_id).outerjoin(RHS, RHS.id==RHR.rhs_id)\
            .where(and_(RHS.competition_id == competition_id, RHS.event == event, RAGRD.ragr_id == ragr_id)).all()
        # ranking = session.query(RAGRD, RHRD, RHR, RHS).where(and_(RHS.competition_id == competition_id,\
        #     RHS.event == event, RAGRD.ragr_id == ragr_id)).with_entities(RAGRD.id, RAGRD.ragr_id, RHRD.id, RHRD.time).all()
        if len(ranking) > 0:
            ranking = pd.DataFrame(ranking, columns=ranking_col)
            ranking['ranking'] = ranking['time'].rank().astype(int)
            for idx, each_rank in ranking.iterrows():
                ragrd_id = each_rank['ragrd_id']
                update_ragrd_rank = session.query(RAGRD).where(RAGRD.id == ragrd_id).first()
                # print(each_rank)
                if each_rank.isna()['ranking']:
                    rank_score = 0
                else:
                    skater_rank = each_rank['ranking']
                    if skater_rank < 9:
                        rank_score = session.query(Score).where(Score.rank == skater_rank).first().point
                    else:
                        rank_score = 0 #score should be 0 if the skater didn't place within 8
                    update_ragrd_rank.rank = skater_rank
                update_ragrd_rank.score = rank_score
                session.commit()
    session.close()

# def score_competition_age_group_result(competit)

def create_competition_age_group_result(competition_id: int, engine: Engine) -> None:
    session = prep_session(engine=engine)
    competition_name = session.query(Competition).where(Competition.id == competition_id).first().name
    ag_genders = session.query(Competition_Skater.ag_id, Competition_Skater.gender_id)\
        .where(Competition_Skater.competition_id == competition_id).distinct().all()
    for agg in ag_genders:
        ag_id = agg.ag_id
        gender_id = agg.gender_id
        print(ag_id, gender_id)
        age_group_name = session.query(Age_Group).where(Age_Group.id == ag_id).first().name
        gender_name = session.query(Gender).where(Gender.id == gender_id).first().name
        report_name = f"{competition_name} {gender_name} {age_group_name} Result"
        if not session.query(exists().where(and_(CAGR.competition_id == competition_id, CAGR.ag_id == ag_id, CAGR.gender_id == gender_id))).scalar():
            new_CAGR = Competition_Age_Group_Result(competition_id=competition_id, ag_id = ag_id, gender_id=gender_id, name=report_name)
            session.add(new_CAGR)
            session.commit()
    session.close()

def create_competition_age_group_result_detail(competition_id: int, engine: Engine) -> None:
    session = prep_session(engine=engine)
    age_group_genders = session.query(CAGR.id, CAGR.ag_id, CAGR.gender_id).where(CAGR.competition_id==competition_id).distinct().all()
    # pd.read_sql_query(age_group_genders_qry, con=engine)
    for agg in age_group_genders:

        event_scores = {}
        cagr_id = agg.id
        ag_id = agg.ag_id 
        gender_id = agg.gender_id

        ragr_ids = session.query(RAGR.id).where(and_(RAGR.competition_id==competition_id,\
            RAGR.ag_id==ag_id, RAGR.gender_id == gender_id)).distinct().all()
        #print(races)
        for each_race in ragr_ids:

        # for idx, each_race in races.iterrows():
            ragr_id = each_race.id
            records = session.query(RHRD.skater_id, RAGRD.score).outerjoin(RHRD, RHRD.id==RAGRD.rhrd_id)\
                .where(RAGRD.ragr_id == ragr_id).all()
            for record in records:
                skater_id = record.skater_id
                score = record.score
                # print(score)
  
                if skater_id in event_scores.keys():
                    event_scores[skater_id] += score
                else:
                    event_scores[skater_id] = score
            # print(event_scores)
            # print(skater_id, event_scores[skater_id])
        for skater_id in event_scores.keys():
            print(skater_id, event_scores[skater_id])
            if not session.query(exists().where(and_(CAGRD.cagr_id == cagr_id, CAGRD.skater_id == skater_id))).scalar():    
                print(skater_id, event_scores[skater_id])
                new_cagrd = Competition_Age_Group_Result_Detail(cagr_id=cagr_id, skater_id=skater_id, total_score=event_scores[skater_id])
                session.add(new_cagrd)
                session.commit()
    session.close()



def rank_competition_age_group_result(competition_id: int, engine: Engine) -> None:
    session = prep_session(engine=engine)
    # cagr = pd.read_sql_query(f'select distinct id from competition_age_group_result where competition_id = {competition_id}', engine)
    #Get all CAGR records for the competition
    cagr = session.query(CAGR.id).where(CAGR.competition_id == competition_id).distinct().all()
    #Get 

    for each_cagr in cagr:
        cagr_id = each_cagr.id
        # ranking = pd.read_sql_query(f'select * from competition_age_group_result_detail where cagr_id = {cagr_id}', engine)
        ranking = session.query(CAGRD.id, CAGRD.cagr_id, CAGRD.skater_id, CAGRD.total_score, CAGRD.rank).where(CAGRD.cagr_id == cagr_id).all()
        ranking_col = ['id', 'cagr_id', 'skater_id', 'total_score','rank']

        if len(ranking) >0:
            ranking = pd.DataFrame(ranking, columns=ranking_col)
            ranking['rank'] = ranking['total_score'].rank(ascending=False).astype(int)
            # ranking['rank'] = ranking['rank'].astype(int)
            for idx, each_rank in ranking.iterrows():
                cagrd_id = each_rank['id']
                skater_rank = each_rank['rank']
                print(type(skater_rank))
                update_cagrd = session.query(CAGRD).where(CAGRD.id == cagrd_id).first()
                update_cagrd.rank = skater_rank
                session.commit()
    session.close()


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

def check_skater(skater: dict, engine: Engine) -> bool:
    session = prep_session(engine=engine)
    #skater dict should contain incomplete info so check based on supplied info
    skater_info = {key: value for key, value in skater.items() if value is not None}
    where_clause = ''
    for key in skater_info.keys():
        if len(where_clause) == 0:
            where_clause += f'Skater.{key} == {key}'
        else:
            where_clause += f', Skater.{key} == {key}'
    return session.query(exists().where(and_(*where_clause))).scalar()

