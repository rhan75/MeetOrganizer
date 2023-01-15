#import sqlite3
from sqlalchemy import create_engine, Float, Table, Column, Integer, String, MetaData, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import toml
import pandas as pd

meta = MetaData()

score = Table(
    'score', meta,
    Column('id', Integer, primary_key = True),
    Column('rank', Integer),
    Column('point', Integer),
)
skater = Table(
    'skater', meta,
    Column('id', Integer, primary_key = True),
    Column('club_id', Integer, ForeignKey('club.id'), nullable=True),
    Column('gender_id', Integer, ForeignKey('gender.id'), nullable=False),
    Column('club_member_number', Integer),
    Column('first_name', String),
    Column('last_name', String),
    Column('dob', Date),
    Column('ngb_member_number', Integer),
    Column('ngb_name', String),
)

skater_Team = Table(
    'skater_team', meta,
    Column('id', Integer, primary_key = True),
    Column('skater1_id', Integer, ForeignKey('skater.id'), nullable=False),
    Column('skater2_id', Integer, ForeignKey('skater.id'), nullable=False),
    Column('skater3_id', Integer, ForeignKey('skater.id'), nullable=False),
    Column('skater4_id', Integer, ForeignKey('skater.id'), nullable=False),
    Column('team_name', String)
)

club = Table(
    'club', meta,
    Column('id', Integer, primary_key = True),
    #Column('state_id', Integer, ForeignKey('State.state_id'), nullable=True),
    #Column('country_id', Integer, ForeignKey('Country.country_id'), nullable=True),
    Column('us_based', Boolean),
    Column('name', String),
    Column('abbreviation', String),
)

State = Table(
    'State', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
    Column('abbreviation', String),
)

Country = Table(
    'Country', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
    Column('abbreviation', String),
)
status = Table(
    'status', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
)

age_group = Table(
    'age_group', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
    Column('min_age', Integer),
    Column('max_age', Integer),
)

age_group_Class = Table(
    'age_group_Class', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
)
gender = Table(
    'gender', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
)

lane = Table(
    'lane', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
)

race_style = Table(
    'race_style', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
)


race = Table(
    'race', meta,
    Column('id', Integer, primary_key = True),
    Column('rs_id', Integer, ForeignKey('race_style.id'), nullable=False),
    Column('name', String),
    Column('distance', Integer),
    Column('team', Boolean),
)

competition = Table(
    'competition', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
    Column('start_date', Date),
    Column('end_date', Date),
)

competition_skater = Table(
    'competition_skater', meta,
    Column('id', Integer, primary_key = True),
    Column('competition_id', Integer, ForeignKey('competition.id'), nullable=False),
    Column('skater_id', Integer, ForeignKey('skater.id'), nullable=False),
    Column('age_group_id', Integer, ForeignKey('age_group.id'), nullable=False),
    Column('gender_id', Integer, ForeignKey('gender.id'), nullable=False),
)

heat = Table(
    'heat', meta,
    Column('id', Integer, primary_key = True),
    Column('name', String),
)

race_heat_schedule = Table(
    'race_heat_schedule', meta,
    Column('id', Integer, primary_key = True),
    Column('race_id', Integer, ForeignKey('race.id'), nullable=False),
    Column('heat_id', Integer, ForeignKey('heat.id'), nullable=False),
    Column('competition_id', Integer, ForeignKey('competition.id'), nullable=False),
    Column('event', Integer),
    Column('name', String),
    Column('total_skaters', Integer),
    Column('team_race', Boolean),
)

race_heat_schedule_detail = Table(
    'race_heat_schedule_Detail', meta,
    Column('id', Integer, primary_key = True),
    Column('race_heat_schedule_id', Integer, ForeignKey('race_heat_schedule.id'), nullable=False),
    Column('skater_team_id', Integer, ForeignKey('skater_team.id'), nullable=True),
    Column('skater_id', Integer, ForeignKey('skater.id'), nullable=True),
    Column('lane_id', Integer, ForeignKey('lane.id'), nullable=False),
)

race_heat_result = Table(
    'race_heat_result', meta,
    Column('id', Integer, primary_key = True),
    Column('race_heat_schedule_id', Integer, ForeignKey('race_heat_schedule.id'), nullable=False),
    Column('race_timestamp', Time)
)

race_heat_result_detail = Table(
    'race_heat_result_Detail', meta,
    Column('id', Integer, primary_key = True),
    Column('race_heat_result_id', Integer, ForeignKey('race_heat_result.id'), nullable=False),
    Column('skater_team_id', Integer, ForeignKey('skater_team.id'), nullable=True),
    Column('skater_id', Integer, ForeignKey('skater.id'), nullable=True),
    Column('lane_id', Integer, ForeignKey('lane.id'), nullable=False),
    Column('status_id', Integer, ForeignKey('status.id'), nullable=False),
    Column('age_group_id', Integer, ForeignKey('age_group.id'), nullable=False),
    Column('gender_id', Integer, ForeignKey('gender.id'), nullable=False),
    Column('time_type', String),
    Column('time', Time),
    Column('time_in_seconds', Float),
    Column('rank', Integer),
)

race_age_group_result = Table(
    'race_age_group_result', meta,
    Column('id', Integer, primary_key = True),
    Column('competition_id', Integer, ForeignKey('competition.id'), nullable=False),
    Column('age_group_id', Integer, ForeignKey('age_group.id'), nullable=False),
    Column('race_id', Integer, ForeignKey('race.id'), nullable=False),
    #Column('dc_id', Integer, ForeignKey('age_group_Class.dc_id'), nullable=False),
    Column('gender_id', Integer, ForeignKey('gender.id'), nullable=False),
    Column('name', String),
)

race_age_group_result_Detail = Table(
    'race_age_group_result_Detail', meta,
    Column('id', Integer, primary_key = True),
    Column('race_age_group_result_id', Integer, ForeignKey('race_age_group_result.id'), nullable=False),
    Column('race_heat_result_detail_id', Integer, ForeignKey('race_heat_result_Detail.id'), nullable=False),
    Column('time_in_seconds', Float), #in seconds
    Column('rank', Integer),
    Column('score', Integer),
)

competition_age_group_result = Table(
    'competition_age_group_result', meta,
    Column('id', Integer, primary_key = True),
    Column('competition_id', Integer, ForeignKey('competition.id'), nullable=False),
    Column('age_group_id', Integer, ForeignKey('age_group.id'), nullable=False),
    Column('gender_id', Integer, ForeignKey('gender.id'), nullable=False),
    Column('name', String),
)

competition_age_group_result_Detail = Table(
    'competition_age_group_result_Detail', meta,
    Column('id', Integer, primary_key = True),
    Column('competition_age_group_result_id', Integer, ForeignKey('competition_age_group_result.id'), nullable=False),
    Column('skater_id', Integer, ForeignKey('skater.id'), nullable=False),
    Column('total_score', Integer),
    Column('rank', Integer),
)
#engine = create_engine('sqlite:///competition_program.db', echo=True)

def create_db():
    meta.create_all(engine)

def populate_db():
    age_group_class_db = pd.read_csv('./csv/age_group_class.csv')
    score_db = pd.read_csv('./csv/score.csv')
    #print(class_db)
    country_db = pd.read_csv('./csv/country.csv')
    age_group_db = pd.read_csv('./csv/age_group.csv')
    heat_db = pd.read_csv('./csv/heat.csv')
    gender_db = pd.read_csv('./csv/gender.csv')
    lane_db = pd.read_csv('./csv/lane.csv')
    race_style_db = pd.read_csv('./csv/race_style.csv')
    race_db = pd.read_csv('./csv/race.csv')
    state_db = pd.read_csv('./csv/state.csv')
    skater_db = pd.read_csv('./csv/skater.csv')
    club_db = pd.read_csv('./csv/club.csv')
    competition_db = pd.read_csv('./csv/competition.csv')
    status_db = pd.read_csv('./csv/status.csv')

    age_group_db.to_sql('age_group', engine, index=False, if_exists='append')
    heat_db.to_sql('heat', engine, index=False, if_exists='append')
    race_style_db.to_sql('race_style', engine, index=False, if_exists='append')
    state_db.to_sql('State', engine, index=False, if_exists='append')
    country_db.to_sql('Country', engine, index=False, if_exists='append')
    gender_db.to_sql('gender', engine, index=False, if_exists='append')
    race_db.to_sql('race', engine, index=False, if_exists='append')
    age_group_class_db.to_sql('age_group_class', engine, index=False, if_exists='append')
    lane_db.to_sql('lane', engine, index=False, if_exists='append')
    club_db.to_sql('club', engine, index=False, if_exists='append')
    skater_db.to_sql('skater', engine, index=False, if_exists='append')
    competition_db.to_sql('competition', engine, index=False, if_exists='append')
    status_db.to_sql('status', engine, index=False, if_exists='append')
    score_db.to_sql('score', engine, index=False, if_exists='append')


if __name__=="__main__":
    with open('config/config.toml', 'r') as config_value:
        config = toml.load(config_value)
    engine = create_engine(f"{config['database']['protocol']}://{config['auth']['username']}:{config['auth']['password']}@{config['server']['host']}:{config['database']['port']}/{config['database']['db']}")
    # engine = create_engine('sqlite:///skatecompetition.db')
    if not database_exists(engine.url):
        create_database(engine.url)
    
    create_db()
    populate_db()