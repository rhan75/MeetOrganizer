#import sqlite3
from sqlalchemy import create_engine, Float, Table, Column, Integer, String, MetaData, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import toml
import pandas as pd

meta = MetaData()

Score = Table(
    'Score', meta,
    Column('score_ID', Integer, primary_key = True),
    Column('rank', Integer),
    Column('point', Integer),
)
Skater = Table(
    'Skater', meta,
    Column('skater_ID', Integer, primary_key = True),
    Column('club_ID', Integer, ForeignKey('Club.club_ID'), nullable=True),
    Column('gender_ID', Integer, ForeignKey('Gender.gender_ID'), nullable=False),
    Column('club_member_number', Integer),
    Column('first_name', String),
    Column('last_name', String),
    Column('dob', Date),
    Column('active', Boolean),
    Column('ngb_member_number', Integer),
    Column('seed_speed', Float),
    Column('seed_distance', Integer),
)

Skater_Team = Table(
    'Skater_Team', meta,
    Column('st_ID', Integer, primary_key=True),
    Column('skater1_skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=False),
    Column('skater2_skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=False),
    Column('skater3_skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=False),
    Column('skater4_skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=False),
    Column('team_name', String)
)

Club = Table(
    'Club', meta,
    Column('club_ID', Integer, primary_key = True),
    Column('state_ID', Integer, ForeignKey('State.state_ID'), nullable=True),
    Column('country_ID', Integer, ForeignKey('Country.country_ID'), nullable=True),
    Column('us_based', Boolean),
    Column('name', String),
    Column('abbreviation', String),
)

State = Table(
    'State', meta,
    Column('state_ID', Integer, primary_key = True),
    Column('name', String),
    Column('abbreviation', String),
)

Country = Table(
    'Country', meta,
    Column('country_ID', Integer, primary_key = True),
    Column('name', String),
    Column('abbreviation', String),
)
Status = Table(
    'Status', meta,
    Column('status_ID', Integer, primary_key = True),
    Column('name', String),
)

Division = Table(
    'Division', meta,
    Column('division_ID', Integer, primary_key = True),
    Column('name', String),
    Column('min_age', Integer),
    Column('max_age', Integer),
)

Division_Class = Table(
    'Division_Class', meta,
    Column('dc_ID', Integer, primary_key = True),
    Column('name', String),
)
Gender = Table(
    'Gender', meta,
    Column('gender_ID', Integer, primary_key = True),
    Column('name', String),
)

Lane = Table(
    'Lane', meta,
    Column('lane_ID', Integer, primary_key = True),
    Column('name', String),
)

Race_Style = Table(
    'Race_Style', meta,
    Column('rs_ID', Integer, primary_key = True),
    Column('name', String),
)


Race = Table(
    'Race', meta,
    Column('race_ID', Integer, primary_key = True),
    Column('rs_ID', Integer, ForeignKey('Race_Style.rs_ID'), nullable=False),
    Column('name', String),
    Column('distance', Integer),
    Column('team', Boolean),
)

Meet = Table(
    'Meet', meta,
    Column('meet_ID', Integer, primary_key = True),
    Column('name', String),
    Column('start_date', Date),
    Column('end_date', Date),
)

Meet_Skater = Table(
    'Meet_Skater', meta,
    Column('ms_ID', Integer, primary_key = True),
    Column('meet_ID', Integer, ForeignKey('Meet.meet_ID'), nullable=False),
    Column('skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=False),
    Column('division_ID', Integer, ForeignKey('Division.division_ID'), nullable=False),
    Column('gender_ID', Integer, ForeignKey('Gender.gender_ID'), nullable=False),
)

Heat = Table(
    'Heat', meta,
    Column('heat_ID', Integer, primary_key = True),
    Column('name', String),
)

Race_Heat_Schedule = Table(
    'Race_Heat_Schedule', meta,
    Column('rhs_ID', Integer, primary_key = True),
    Column('race_ID', Integer, ForeignKey('Race.race_ID'), nullable=False),
    Column('heat_ID', Integer, ForeignKey('Heat.heat_ID'), nullable=False),
    Column('meet_ID', Integer, ForeignKey('Meet.meet_ID'), nullable=False),
    Column('name', String),
    Column('total_skaters', Integer),
    Column('team_race', Boolean),
)

Race_Heat_Schedule_Detail = Table(
    'Race_Heat_Schedule_Detail', meta,
    Column('rhsd_ID', Integer, primary_key = True),
    Column('rhs_ID', Integer, ForeignKey('Race_Heat_Schedule.rhs_ID'), nullable=False),
    Column('st_ID', Integer, ForeignKey('Skater_Team.st_ID'), nullable=True),
    Column('skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=True),
    Column('lane_ID', Integer, ForeignKey('Lane.lane_ID'), nullable=False),
)

Race_Heat_Result = Table(
    'Race_Heat_Result', meta,
    Column('rhr_ID', Integer, primary_key = True),
    Column('rhs_ID', Integer, ForeignKey('Race_Heat_Schedule.rhs_ID'), nullable=False),
    Column('race_timestamp', Time)
)

Race_Heat_Result_Detail = Table(
    'Race_Heat_Result_Detail', meta,
    Column('rhrd_ID', Integer, primary_key = True),
    Column('rhr_ID', Integer, ForeignKey('Race_Heat_Result.rhr_ID'), nullable=False),
    Column('st_ID', Integer, ForeignKey('Skater_Team.st_ID'), nullable=True),
    Column('skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=True),
    Column('lane_ID', Integer, ForeignKey('Lane.lane_ID'), nullable=False),
    Column('status_ID', Integer, ForeignKey('Status.status_ID'), nullable=False),
    Column('division_ID', Integer, ForeignKey('Division.division_ID'), nullable=False),
    Column('gender_ID', Integer, ForeignKey('Gender.gender_ID'), nullable=False),
    Column('time_type', String),
    Column('time', Time),
    Column('time_in_seconds', Float),
    Column('rank', Integer),
)

Race_Division_Result = Table(
    'Race_Division_Result', meta,
    Column('rdr_ID', Integer, primary_key = True),
    Column('meet_ID', Integer, ForeignKey('Meet.meet_ID'), nullable=False),
    Column('division_ID', Integer, ForeignKey('Division.division_ID'), nullable=False),
    Column('race_ID', Integer, ForeignKey('Race.race_ID'), nullable=False),
    #Column('dc_ID', Integer, ForeignKey('Division_Class.dc_ID'), nullable=False),
    Column('gender_ID', Integer, ForeignKey('Gender.gender_ID'), nullable=False),
    Column('name', String),
)

Race_Division_Result_Detail = Table(
    'Race_Division_Result_Detail', meta,
    Column('rdrd_ID', Integer, primary_key = True),
    Column('rdr_ID', Integer, ForeignKey('Race_Division_Result.rdr_ID'), nullable=False),
    Column('rhrd_ID', Integer, ForeignKey('Race_Heat_Result_Detail.rhrd_ID'), nullable=False),
    Column('time_in_seconds', Float), #in seconds
    Column('rank', Integer),
    Column('score', Integer),
)

Meet_Division_Result = Table(
    'Meet_Division_Result', meta,
    Column('mdr_ID', Integer, primary_key = True),
    Column('meet_ID', Integer, ForeignKey('Meet.meet_ID'), nullable=False),
    Column('division_ID', Integer, ForeignKey('Division.division_ID'), nullable=False),
    Column('gender_ID', Integer, ForeignKey('Gender.gender_ID'), nullable=False),
    Column('name', String),
)

Meet_Division_Result_Detail = Table(
    'Meet_Division_Result_Detail', meta,
    Column('mdrd_ID', Integer, primary_key = True),
    Column('mdr_ID', Integer, ForeignKey('Meet_Division_Result.mdr_ID'), nullable=False),
    Column('skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=False),
    Column('total_score', Integer),
    Column('rank', Integer),
)
#engine = create_engine('sqlite:///meet_program.db', echo=True)

def create_db():
    meta.create_all(engine)

def populate_db():
    division_class_db = pd.read_csv('./csv/division_class.csv')
    score_db = pd.read_csv('./csv/score.csv')
    #print(class_db)
    country_db = pd.read_csv('./csv/country.csv')
    division_db = pd.read_csv('./csv/Divisions.csv')
    heat_db = pd.read_csv('./csv/heat.csv')
    gender_db = pd.read_csv('./csv/gender.csv')
    lane_db = pd.read_csv('./csv/lane.csv')
    race_style_db = pd.read_csv('./csv/race_style.csv')
    race_db = pd.read_csv('./csv/race.csv')
    state_db = pd.read_csv('./csv/state.csv')
    skater_db = pd.read_excel('./csv/PSSC member profile for 2022_2023.xlsx')
    skater_db['dob'] = skater_db.apply(lambda row: row['MM/DD'].replace(year=row['YYYY']), axis=1)
    skater_db['club_member_number'] = skater_db.apply(lambda row: row['pssc_num'] if row['pssc_num'] else 0, axis=1)
    skater_db['ngb_member_number'] = skater_db['uss_num']
    skater_db['gender_ID'] = skater_db.apply(lambda row: 1 if row['gender'] == 'M' else 2, axis=1)
    skater_db['club_ID'] = 1
    skater_db['active'] = True
    skater_db = skater_db.drop(columns=['MM/DD', 'YYYY', 'uss_num', 'pssc_num', 'gender', 'guest_num'])
    club_db = pd.read_csv('./csv/club.csv')
    meet_db = pd.read_csv('./csv/meet.csv')
    status_db = pd.read_csv('./csv/status.csv')

    division_db.to_sql('Division', engine, index=False, if_exists='append')
    heat_db.to_sql('Heat', engine, index=False, if_exists='append')
    race_style_db.to_sql('Race_Style', engine, index=False, if_exists='append')
    state_db.to_sql('State', engine, index=False, if_exists='append')
    country_db.to_sql('Country', engine, index=False, if_exists='append')
    gender_db.to_sql('Gender', engine, index=False, if_exists='append')
    race_db.to_sql('Race', engine, index=False, if_exists='append')
    division_class_db.to_sql('Division_Class', engine, index=False, if_exists='append')
    lane_db.to_sql('Lane', engine, index=False, if_exists='append')
    club_db.to_sql('Club', engine, index=False, if_exists='append')
    skater_db.to_sql('Skater', engine, index=False, if_exists='append')
    meet_db.to_sql('Meet', engine, index=False, if_exists='append')
    status_db.to_sql('Status', engine, index=False, if_exists='append')
    score_db.to_sql('Score', engine, index=False, if_exists='append')


if __name__=="__main__":
    with open('config/config.toml', 'r') as config_value:
        config = toml.load(config_value)
    engine = create_engine(f"{config['database']['protocol']}://{config['auth']['username']}:{config['auth']['password']}@{config['server']['host']}:{config['database']['port']}/{config['database']['db']}")
    if not database_exists(engine.url):
        create_database(engine.url)
    
    create_db()
    populate_db()