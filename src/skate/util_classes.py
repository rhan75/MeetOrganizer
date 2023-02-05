from dataclasses import dataclass
from sqlalchemy.engine.base import Engine
from sqlalchemy import exists, and_
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.orm import decl_api, session
import pandas as pd
from datetime import timedelta, date, datetime
from models.model import *

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

def get_race_age_group_gender_race(competition_id, event, session):
    return session.query(RHS.race_id, RHRD.ag_id, RHRD.gender_id)\
        .outerjoin(RHR, RHS.id == RHR.rhs_id)\
        .outerjoin(RHRD, RHR.id == RHRD.rhr_id)\
        .filter(and_(RHS.competition_id == competition_id, RHS.event == event))\
        .distinct().order_by(RHRD.ag_id).all()

@dataclass
class RaceResult:
    skater_id: int
    race_id: int
    heat_id: int
    competition_id: int
    lane_id: int
    gender_id: int 
    ag_id: int
    event: int
    status_id: int
    heat_rank: int
    timing_type: str
    race_name: str
    time: str


class RaceScheduleService:
    def __init__(self, engine: Engine):
        self.engine = engine

class RaceHeatResultService:
    def __init__(self, engine: Engine):
        self.engine = engine
    
    

class RaceAgeGroupResultService:
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_race_age_group_result(self, race_result: RaceResult):
        session = prep_session(self.engine)
        competition_id = race_result.competition_id
        event = race_result.event
        AGGR = get_race_age_group_gender_race(competition_id, event, session)
        for row in AGGR:
            ag_id = row.ag_id
            gender_id = row.gender_id
            race_id = row.race_id
            # if not self.session.query(exists().where(and_(RAGR.ag_id == ag_id, RAGR.competition_id == competition_id, RAGR.gender_id == gender_id, RAGR.event == event))).scalar():
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

    def create_race_age_group_result_detail(self, competition_id: int, event: int, race_id: int) -> None:
        session = prep_session(self.engine)

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
