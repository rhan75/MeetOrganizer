#import sqlite3
from sqlalchemy import create_engine, Float, Table, Column, Integer, String, MetaData, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import toml

with open('config/config.toml', 'r') as config_value:
    config = toml.load(config_value)
engine = create_engine(f"{config['database']['protocol']}://{config['auth']['username']}:{config['auth']['password']}@{config['server']['host']}:{config['database']['port']}/{config['database']['db']}")
if not database_exists(engine.url):
    create_database(engine.url)
#engine = create_engine('sqlite:///meet_program.db', echo=True)
meta = MetaData()

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

Gender = Table(
    'Gender', meta,
    Column('gender_ID', Integer, primary_key = True),
    Column('name', String),
)

Lane = Table(
    'Lane', meta,
    Column('lane_ID', Integer, primary_key = True),
    Column('name', String),
    Column('number', Integer),
    Column('location', String),
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
    Column('meetID_ID', Integer, ForeignKey('Meet.meet_ID'), nullable=False),
    Column('name', String),
    Column('total_skaters', Integer),
    Column('team_race', Boolean),
)

Race_Heat_Result = Table(
    'Race_Heat_Result', meta,
    Column('rhr_ID', Integer, primary_key = True),
    Column('rhs_ID', Integer, ForeignKey('Race_Heat_Schedule.rhs_ID'), nullable=False),
    Column('race_timestamp', Time)
)


Race_Heat_Sechedule_Detail = Table(
    'Race_Heat_Schedule_Detail', meta,
    Column('rhsd_ID', Integer, primary_key = True),
    Column('rhr_ID', Integer, ForeignKey('Race_Heat_Result.rhr_ID'), nullable=False),
    Column('st_ID', Integer, ForeignKey('Skater_Team.st_ID'), nullable=True),
    Column('skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=True),
    Column('lane_ID', Integer, ForeignKey('Lane.lane_ID'), nullable=False),
    Column('race_time', Time),
    Column('rank', Integer),
)

Race_Heat_Result_Detail = Table(
    'Race_Heat_Result_Detail', meta,
    Column('rhrd_ID', Integer, primary_key = True),
    Column('rhs_ID', Integer, ForeignKey('Race_Heat_Schedule.rhs_ID'), nullable=False),
    Column('st_ID', Integer, ForeignKey('Skater_Team.st_ID'), nullable=True),
    Column('skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=True),
    Column('lane_ID', Integer, ForeignKey('Lane.lane_ID'), nullable=False),
    Column('status_ID', Integer, ForeignKey('Status.status_ID'), nullable=False),
    Column('race_time', Time),
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

Race_Division_Result = Table(
    'Race_Division_Result', meta,
    Column('rdr_ID', Integer, primary_key = True),
    Column('meet_ID', Integer, ForeignKey('Meet.meet_ID'), nullable=False),
    Column('division_ID', Integer, ForeignKey('Division.division_ID'), nullable=False),
    Column('race_ID', Integer, ForeignKey('Race.race_ID'), nullable=False),
    Column('dc_ID', Integer, ForeignKey('Division_Class.dc_ID'), nullable=False),
    Column('gender_ID', Integer, ForeignKey('Gender.gender_ID'), nullable=False),
    Column('name', String),
)

Race_Division_Result_Detail = Table(
    'Race_Division_Result_Detail', meta,
    Column('rdrd_ID', Integer, primary_key = True),
    Column('rdr_ID', Integer, ForeignKey('Race_Division_Result.rdr_ID'), nullable=False),
    Column('rhrd_ID', Integer, ForeignKey('Race_Heat_Result_Detail.rhrd_ID'), nullable=False),
    Column('rank', Integer),
    Column('score', Integer),
)

Meet_Result = Table(
    'Meet_Result', meta,
    Column('mr_ID', Integer, primary_key = True),
    Column('meet_ID', Integer, ForeignKey('Meet.meet_ID'), nullable=False),
    Column('division_ID', Integer, ForeignKey('Division.division_ID'), nullable=False),
    Column('gender_ID', Integer, ForeignKey('Gender.gender_ID'), nullable=False),
    Column('name', String),
)

Meet_Result_Detail = Table(
    'Meet_Result_Detil', meta,
    Column('mrd_ID', Integer, primary_key = True),
    Column('mr_ID', Integer, ForeignKey('Meet_Result.mr_ID'), nullable=False),
    Column('skater_ID', Integer, ForeignKey('Skater.skater_ID'), nullable=False),
    Column('total_score', Integer),
    Column('rank', Integer),
)

def create_db():
    meta.create_all(engine)


if __name__=="__main__":
    create_db()