# from dataclasses import dataclass
from sqlalchemy.engine.base import Engine
from sqlalchemy import exists, and_, desc
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.orm import decl_api, session
import pandas as pd
from datetime import timedelta, date, datetime
from models.model import *
from models.aliases import *

def is_valid_time(time_string):
    '''
    Get time_string
    Check if it is in %M:%S.%f format
    and return True
    If not, return False
    '''
    try:
        time_format = '%M:%S.%f'
        datetime.strptime(time_string, time_format)
        return True
    except ValueError:
        return False

def update_object(session: session.Session, model_name: decl_api.DeclarativeMeta, model_dict: dict, main_keys: dict):
    '''
    Return result of update status: 
    Duplicates - Multiple records - Need to check and change
    Conflict - 1 record exist but properties don't match
    Exist - 1 match record
    Added - Inserted a new record
    '''
    instance = get_object_info(session, model_name, **main_keys)
    if len(instance) == 1:
        if not compare_dict_instance(model_dict, instance): 
        #instance and info doesn't match:    
            result = 'Conflict'
        else:
        #instance and info matches
            result = 'Exist'
    elif len(instance) == 0:
        #Instance doesn't exist. Must add the record
        new_instance = model_name(**model_dict)
        session.add(new_instance)
        session.commit()
        result = 'Added'
        session.close()
    else:
        result = 'Duplicates'

    return result

def compare_dict_instance(dict_obj, class_instance):
    '''
    Check dict with class instance
    False - dict and instance don't match
    True - All properties match
    '''
    for key, value in dict_obj.items():
        if hasattr(class_instance, key):
            if getattr(class_instance, key) != value:
                return False
        else:
            return False
    return True

def get_object_info(session, model_name, **kwargs):
    '''
    Return list of rows from model_name based on keyward arguments
    '''
    query = session.query(model_name)
    if kwargs:
        for attr, value in kwargs.items():
            query = query.filter(getattr(model_name, attr) == value)
    result = query.all()
    session.close()
    return result

def prep_session(engine: Engine) -> sessionmaker:
    '''
    Provide session
    '''
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def find_skating_age(dob: date) -> int:
    '''
    Get the Skating Age based on the supplied DOB
    Skate Age Cutoff 6/30 of each year
    If today is after 6/30, the current year is the skating year.
    If before 6/30, then the skatting year is one year less than the current year. 
    Using that info, find the date difference between the DOB and the skating cut off year.
    The skating age of the skater should be the date difference / 365.2425 = year.fraction
    Return year portion only.
    '''
    current_date = date.today()
    if current_date.month >= 7:
        skating_year = current_date.year
    else:
        skating_year = current_date.year - 1
    skating_age_date = date(skating_year, 6, 30)

    return int(int((skating_age_date - dob).days) / 365.2425)

def find_age_group(age:int, session: session.Session) -> int:
    '''
    Using age of the skater
    Return the record where age_group's min_age <= age <= max_age. 
    '''
    age_group_info = session.query(Age_Group).filter(and_(Age_Group.min_age <= age, Age_Group.max_age >= age)).first()
    session.close()
    return age_group_info

def find_schedule_info(race_info: str) -> dict:  # Checked
    '''
    From the race_info constructed from the SprintTimer schedule import file,
    Extract heat / event / round / date / name of the comp / distance / race style info.
    Construct schedule info dict.
    Return the resulting dict
    '''
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
    '''
    From the schedule import file
    Construct heat info 
    '''
    heat = []
    heats = []
    for line in lines:
        if '#' not in line:
            heat.append(line)
        else:
            heats.append(heat)
            heat = []
    return heats

def import_schedule(schedule_path: str, engine: Engine) -> dict:  # Checked
    '''
    Open the schedule file.
    Read lines of the schedule file.
    Pass lines to get_heat_schedule.
    Get heats dict of all heat information from lines.
    Enumerate each heat from heats dict:
        Get race_info and get race detail using find_schedule_info.
        Get each skater info from heat info.
        Construct skater_info dict.
        Add skater_info into race_heat_schedule dict
    Repeat until all heats are processed.
    Pass race_heat_schedules dict to create_race_heat_schedule_and_detail
    '''
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
            #Maybe check if the skater info is correct? 
            skater = skater.split(',')
            skater_info['skater_num'] = skater[0]
            skater_info['lane_num'] = skater[1]
            skater_info['first_name'] = skater[2]
            skater_info['last_name'] = skater[3]
            skater_info['club'] = skater[4][:-1]
            heat_skaters.append(skater_info)
        race_heat_schedules[f'race{idx}'] = {
            'heat_info': heat_info, 'skaters': heat_skaters}
    # return race_heat_schedules
    create_race_heat_schedule_and_detail(race_heat_schedules, engine)

def create_race_heat_schedule_and_detail(race_heat_schedules: dict, engine: Engine) -> None:
    '''
    
    '''
    session = prep_session(engine=engine)
    for key, each_heat in race_heat_schedules.items():
        total_skaters = len(each_heat['skaters'])
        distance = int(each_heat['heat_info']['distance'])
        event = int(each_heat['heat_info']['event'])
        race_type = each_heat['heat_info']['race_style']
        rs_id = get_object_info(session, Race_Style, name=race_type)[0].id
        current_race = get_object_info(session, Race, distance=distance, rs_id=rs_id)[0]
        race_id = current_race.id
        team_bool = current_race.team
        competition_name = each_heat['heat_info']['competition_name']
        competition_id = get_object_info(session, Competition, name=competition_name)[0].id
        heat_id = get_object_info(session, Heat, name=f"Heat {each_heat['heat_info']['heat']}")[0].id
        heat_name = f"{competition_name}: {current_race.name} Heat {each_heat['heat_info']['heat']}"

        main_keys = {'race_id':race_id, 'heat_id':heat_id, 'competition_id':competition_id,'event':event}
        new_heat_schedule = {'race_id':race_id, 'heat_id':heat_id, 'competition_id':competition_id,'event':event, 'name':heat_name, 'total_skaters':total_skaters, 'team_race':team_bool}
        update_object(session, Race_Heat_Schedule, new_heat_schedule, main_keys)
        
        current_race_heat_schedule = get_object_info(session, RHS, name=heat_name)[0]
        rhs_id = current_race_heat_schedule.id
        for heat_skater in each_heat['skaters']:
            current_skater = get_object_info(session, Skater, club_member_number=heat_skater['skater_num'])[0]
            skater_id = current_skater.id
            lane_id = get_object_info(session, Lane, name=heat_skater['lane_num'])[0].id
            main_keys = {'rhs_id':rhs_id, 'skater_id':skater_id}
            new_rhsd_record = {'rhs_id':rhs_id, 'skater_id':skater_id, 'lane_id':lane_id}
            update_object(session, Race_Heat_Schedule_Detail, new_rhsd_record, main_keys)
            update_competition_skater(competition_id, skater_id, engine)
    session.close()

def update_competition_skater(competition_id: int, skater_id: int, engine: Engine) -> str:
    session = prep_session(engine=engine)
    #Get skater's gender and age info to build main keys dict and skater's info dict
    gender_age = get_object_info(session, Skater, id=skater_id)[0]
    gender_id = gender_age.gender_id
    age = find_skating_age(gender_age.dob)
    age_group = find_age_group(age, session)
    ag_id = age_group.id
    main_keys = {'competition_id': competition_id, 'skater_id': skater_id}
    new_comp_skater = {'competition_id': competition_id, 'skater_id': skater_id,\
        'ag_id': ag_id, 'gender_id':gender_id}
    result = update_object(session, Competition_Skater, new_comp_skater, main_keys)
    session.close()
    return result

def get_heat_result(result_file: str) -> dict:
    '''
    Provide:
    Race name
    Timing Type
    Timestamp
    '''
    heat_result = {}
    with open(result_file, 'r') as result_file:
        lines = result_file.readlines()
    race_heat_schedule_name = f"{lines[0][:-1]} {lines[1].split(',')[0]}"
    heat_result['name'] = race_heat_schedule_name
    timestamp = lines[1].split('  ')[1][:-1]  # Remove \n from the line"
    if 'MT' in timestamp:
        timestamp = '00:00:00 AM'
        time_type = 'manual'
    else:
        time_type = 'automatic'
    timestamp = pd.to_datetime(timestamp).strftime('%H:%M:%S')
    # timestamp = datetime.strptime(timestamp, '%H:%M:%S').time()
    heat_result['time_type'] = time_type
    heat_result['timestamp'] = timestamp
    return heat_result

def create_race_heat_result(result_file: str, engine: Engine) -> dict:  # Checked
    '''
    Import result files
    Get heat info, skater info, timing type, race result time
    '''
    session = prep_session(engine=engine)
    heat_result = get_heat_result(result_file)
    schedule = get_object_info(session, RHS, name=heat_result['name'])[0]
    rhs_id = schedule.id
    main_keys = {'rhs_id': rhs_id}
    race_result = {'rhs_id': rhs_id, 'timestamp':heat_result['timestamp']}
    update_result = update_object(session, Race_Heat_Result, race_result, main_keys)
    if update_result in ['Conflicted', 'Duplicates']:
        return {'status': 'failed'}
    else:
        rhr_id = get_object_info(session, RHR, rhs_id=rhs_id)[0].id
    session.close()
    return {'status': 'success', 'rhr_id': rhr_id, 'time_type': heat_result['time_type']}

def format_time(time_string: str) -> dict:
    if is_valid_time(time_string):
        time_format = '%M:%S.%f'
        time_datetime = datetime.strptime(time_string, time_format)
        time_in_seconds = (time_datetime.minute *60) + time_datetime.second + (time_datetime.microsecond/1000000)
    else:
        time_in_seconds = float(time_string)
    # time_value = timedelta(seconds=time_in_seconds)
    minutes, seconds = divmod(time_in_seconds, 60)
    time_value = "{:02d}:{:06.3f}".format(int(minutes), seconds)
    return {'time_in_seconds': time_in_seconds, 'time_value':time_value}

def create_race_heat_result_detail(result_file: str, rhr_result: dict, engine: Engine) -> None:  # Checked
    session = prep_session(engine=engine)
    rhr_id = rhr_result['rhr_id']
    time_type = rhr_result['time_type']
    COLUMN_NAME = ['rank', 'club_member_number', 'lane', 'name', 'team', 'time']
    datatype = {'rank':str, 'club_member_number': int, 'lane': str, 'name': str, 'team': str, 'time': str}
    result_data = pd.read_csv(result_file, skiprows=2, dtype=datatype, names=COLUMN_NAME, index_col=None)
    for each_result in result_data.iterrows():
        rank = each_result[1]['rank']
        if rank in ['dnf', 'dns']:
            status_id = get_object_info(session, Status, name=rank)[0].id
            rank = None
            time_in_seconds = None
            time_value = None
        else:
            rank = int(rank)
            status_id = get_object_info(session, Status, name='finished')[0].id
            time_string = each_result[1]['time']
            # print(type(time_string), time_string)
            time_dict = format_time(time_string)
            time_in_seconds = time_dict['time_in_seconds']
            time_value = time_dict['time_value']
        st_id = None
        club_member_number = each_result[1]['club_member_number']
        lane_name = each_result[1]['lane'][1:]
        lane_id = get_object_info(session, Lane, name=lane_name)[0].id
        skater_info = get_object_info(session, Skater, club_member_number=club_member_number)[0]
        skater_id = skater_info.id
        gender_id = skater_info.gender_id
        age = find_skating_age(skater_info.dob)
        ag_id = find_age_group(age, session).id
        main_keys = {'rhr_id':rhr_id, 'skater_id': skater_id}
        new_rhrd_record = {
            'rhr_id':rhr_id, 'st_id':st_id, 'skater_id':skater_id, 'lane_id':lane_id,
            'status_id':status_id, 'ag_id':ag_id, 'gender_id':gender_id, 'time_type':time_type, 
            'time': time_value, 'time_in_seconds': time_in_seconds,'rank':rank
        }
        update_object(session, Race_Heat_Result_Detail, new_rhrd_record, main_keys)
    session.close()

def get_race_age_group_gender_race(competition_id, event, session):
    return session.query(RHS.race_id, RHRD.ag_id, RHRD.gender_id)\
        .outerjoin(RHR, RHS.id == RHR.rhs_id)\
        .outerjoin(RHRD, RHR.id == RHRD.rhr_id)\
        .filter(and_(RHS.competition_id == competition_id, RHS.event == event))\
        .distinct().order_by(RHRD.ag_id).all()

def create_race_age_group_result(competition_id: int, event: int, engine: Engine) -> None:  # Checked
    session = prep_session(engine=engine)
    AGGR = get_race_age_group_gender_race(competition_id, event, session)
    for row in AGGR:
        ag_id = row.ag_id
        gender_id = row.gender_id
        race_id = row.race_id
        agc_id = None
        name = (
            f"{get_object_info(session, Competition, id=competition_id)[0].name} "
            f"{get_object_info(session, Gender, id=gender_id)[0].name} "
            f"{get_object_info(session, Age_Group, id=ag_id)[0].name} "
            f"{get_object_info(session, Race, id=race_id)[0].name} "
        )
        main_keys = {'ag_id':ag_id, 'competition_id':competition_id, 'race_id':race_id, 'gender_id':gender_id, 'event':event}
        new_ragr = {
            'ag_id':ag_id, 'competition_id':competition_id, 'race_id':race_id,
            'agc_id':agc_id, 'gender_id':gender_id, 'event':event, 'name':name
            }
        update_object(session, Race_Age_Group_Result, new_ragr, main_keys)
    session.close()

# Checked
def create_race_age_group_result_detail(competition_id: int, event: int, race_id: int, engine: Engine) -> None:
    session = prep_session(engine=engine)

    rhs_ids = session.query(RHS.id).where(and_(RHS.competition_id == competition_id, RHS.race_id == race_id, RHS.event == event)).all()
    kwargs = {'competition_id':competition_id, 'race_id':race_id, 'event':event}
    rhs_ids = get_object_info(session, RHS, **kwargs)
    for row in rhs_ids:
        rhr_id = get_object_info(session, RHR, rhs_id=row.id)[0].id
        rhrd_results = get_object_info(session, RHRD, rhr_id=rhr_id)
        for result in rhrd_results:
            ag_id, rhrd_id, gender_id, time_in_seconds = result.ag_id, result.id, result.gender_id, result.time_in_seconds
            ragr_id_args = {'event':event, 'ag_id':ag_id, 'competition_id':competition_id, 'race_id':race_id, 'gender_id':gender_id}
            ragr_id = get_object_info(session, RAGR, **ragr_id_args)[0].id
            main_keys = {'ragr_id':ragr_id, 'rhrd_id':rhrd_id}
            new_ragrd = {'ragr_id':ragr_id, 'rhrd_id':rhrd_id, 'time_in_seconds':time_in_seconds}
            update_object(session, Race_Age_Group_Result_Detail, new_ragrd, main_keys)
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
        ranking = session.query(RAGRD.id, RAGRD.ragr_id, RHRD.id, RHRD.time_in_seconds).outerjoin(RHRD, RHRD.id==RAGRD.rhrd_id)\
            .outerjoin(RHR, RHR.id == RHRD.rhr_id).outerjoin(RHS, RHS.id==RHR.rhs_id)\
            .where(and_(RHS.competition_id == competition_id, RHS.event == event, RAGRD.ragr_id == ragr_id, RAGRD.time_in_seconds != None)).all()
        if len(ranking) > 0:
            ranking = pd.DataFrame(ranking, columns=ranking_col)
            ranking['ranking'] = ranking['time'].rank().astype(int)
            for idx, each_rank in ranking.iterrows():
                ragrd_id = each_rank['ragrd_id']
                update_ragrd_rank = session.query(RAGRD).where(RAGRD.id == ragrd_id).first()
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
        for each_race in ragr_ids:

        # for idx, each_race in races.iterrows():
            ragr_id = each_race.id
            records = session.query(RHRD.skater_id, RAGRD.score).outerjoin(RHRD, RHRD.id==RAGRD.rhrd_id)\
                .where(RAGRD.ragr_id == ragr_id).all()
            for record in records:
                skater_id = record.skater_id
                score = record.score
                if score:
                    if skater_id in event_scores.keys():
                        event_scores[skater_id] += score
                    else:
                        event_scores[skater_id] = score
        for skater_id in event_scores.keys():
            if not session.query(exists().where(and_(CAGRD.cagr_id == cagr_id, CAGRD.skater_id == skater_id))).scalar():    
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
                update_cagrd = session.query(CAGRD).where(CAGRD.id == cagrd_id).first()
                update_cagrd.rank = skater_rank
                session.commit()
    session.close()


def rank_conflict_resolver(df: pd.DataFrame, competition_id:int, engine: Engine) -> pd.DataFrame:
    '''
    Steps: 
    1. Determine duplicate rankings
    2. Loop over duplicate rankings and get skaters for each dup rank
    3. determine the longest distance race for dup rank skaters.
    4. Calculate the relative ranking of the longest distance of each skater.
    5. Determine the new ranking by (Current_rank + longest_distance_relatvie_rank) - 1
    6. Update the current_rank 
    '''

    dup_ranking = df[df['rank'].duplicated()]
    dup_ranking = dup_ranking['rank'].drop_duplicates()
    conflict_ranking = {}
    for current_rank in dup_ranking:
        skaters = []
        temp_df = df[df['rank'] == current_rank]
        skaters = [row['skater_id'] for idx, row in temp_df.iterrows()]
        conflict_ranking[current_rank] = skaters
        longest_race_id = determine_longest_race(competition_id, skaters)
        # Get the result of session.query for RAGRD with competition_id, race_id, event filter by skaters, rank 




    
    #Determine if how many different ranking exists
    dup_count = dup_ranking['rank'].unique
    if dup_count == 1:
        for idx, dup in dup_ranking.iterrows():
            #Determin the longest race of the competition
            longest_event = longest_race(competition_id, dup.skater_id)
            



    #
    fixed_df = pd.DataFrame()
    return fixed_df
    

def determine_longest_race(competition_id: int, skater_ids: list) -> int:
    '''
    Step
    1. Setr longest_race = 0
    2. Loop over skater_ids.
    3. select race.id, race.distance RHS left join RHSD left join Race filter by competition_id, skater_id
    4. Order by race.distance descending and get the race.id of the first row
    5. if race.distance of the first row is bigger than longest_race, assign longest_race = race.distance
    6. Complete the for loop.
    7. Return lognest_race
    '''
    longest_race = 0
    longest_race_id = None
    for skater_id in skater_ids:
        race_distance = session.query(Race.id, Race.distance)\
            .outerjoin(RHSD, RHSD.rhs_id == RHS.id).outerjoin(Race, Race.id == RHS.race_id)\
            .filter(and_(RHS.competition_id==competition_id, RHRD.skater_id == skater_id))\
            .distinct().order_by(desc(Race.distance)).first()
        if race_distance.distance > longest_race:
            longest_race = race_distance.distance
            longest_race_id = race_distance.id
    return longest_race_id


