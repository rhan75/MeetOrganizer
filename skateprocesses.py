from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Time, Float, ForeignKey, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import toml
import pandas as pd
import json
import csv
from datetime import timedelta
from skate import find_skating_age

def find_schedule_info(race_info: str) -> dict:
    schedule_info = {}
    schedule_info['heat'] = race_info.split(',')[1]
    schedule_info['round'] = race_info.split(',')[2]
    schedule_info['race'] = race_info.split(',')[3]
    schedule_info['date'] = race_info.split(':')[0].split(' ', 1)[0]
    schedule_info['meet_name'] = race_info.split(':')[0]
    schedule_info['distance'] = race_info.split(':')[1].split(' ')[1][:-1]
    schedule_info['race_style'] = race_info.split(':')[1].split(',')[0].split(' ',2)[2]
    return schedule_info


def get_heat_schedule(schedule_path: str) -> list:
    heat = []
    heats = []
    with open(schedule_path, 'r') as schedules:
        lines = schedules.readlines()
    for line in lines:
        if '#' not in line:
            heat.append(line)
        else:
            heats.append(heat)
            heat=[]
    return heats

def create_race_division_result(meet_ID: int, race_ID: int) -> None:
    meet_skater = pd.read_sql_query('select * from "Meet_Skater";', con=engine)
    current_meet_skater_division = pd.read_sql_query('select distinct "division_ID" from "Meet_Skater" where "meet_ID" = 1;', con=engine)
    for each_div in current_meet_skater_division.iterrows():
        division_ID = each_div[1][0]
        gender_ID_list = meet_skater[meet_skater['division_ID']==division_ID]['gender_ID'].unique().tolist()
        for gender_ID in gender_ID_list:
            exist_check = f'select exists(select 1 from "Race_Division_Result" where "division_ID" = {division_ID} and "meet_ID" = {meet_ID} and "gender_ID" = {gender_ID} and "race_ID" = {race_ID});'
            if not engine.execute(exist_check).fetchall()[0][0]:
                name = f"{gender[gender['gender_ID'] == gender_ID].iloc[0]['name']} {division[division['division_ID']==division_ID].iloc[0]['name']} {race[race['race_ID']==race_ID].iloc[0]['name']}"
                qry = f'insert into "Race_Division_Result"("division_ID", "meet_ID", "race_ID", "gender_ID", name) values ({division_ID}, {meet_ID}, {race_ID}, {gender_ID}, \'{name}\')'
                engine.execute(qry)
        

def create_race_division_result_detail(meet_ID: int, race_ID: int) -> None:
    race_heat_schedule = pd.read_sql_query('select * from "Race_Heat_Schedule";', con=engine)
    race_heat_result_detail = pd.read_sql_query('select * from "Race_Heat_Result_Detail";', con=engine)
    race_heat_result = pd.read_sql_query('select * from "Race_Heat_Result";', con=engine)
    rhs_ID_list = race_heat_schedule[(race_heat_schedule['meet_ID']==meet_ID) & (race_heat_schedule['race_ID']==race_ID)]['rhs_ID'].tolist()
    for rhs_ID in rhs_ID_list:
        possible_rhr_ID = race_heat_result[race_heat_result['rhs_ID'] == rhs_ID]
        if not possible_rhr_ID.empty:
            rhr_ID = possible_rhr_ID['rhr_ID'].tolist()[0]
            
        
    

def create_race_heat_schedule_detail(race_heat_schedules: dict) -> None:
    for race_name in race_heat_schedules:
        each_heat = race_heat_schedules[race_name]
        # Construct race_heat_schedule first: race_ID / heat_ID / meet_ID / heat name / total skaters / bool team race
        total_skaters = len(each_heat['skaters'])
        distance = int(each_heat['heat_info']['distance'])
        race_type = each_heat['heat_info']['race_style']
        rs_ID = rs_ID = race_style[race_style['name']==race_type].iloc[0]['rs_ID']
        race_ID = (race[(race['distance'] == distance) & (race['rs_ID'] == int(rs_ID))].iloc[0]['race_ID'])
        team_bool = race[race['race_ID'] == race_ID].iloc[0]['team']
        race_name = (race[(race['distance'] == distance) & (race['rs_ID'] == int(rs_ID))].iloc[0]['name'])
        meet_name = each_heat['heat_info']['meet_name']
        meet_ID = meet[meet['name'] == meet_name].iloc[0]['meet_ID']
        heat_ID = heat[heat['name'] == f"Heat {each_heat['heat_info']['heat']}"].iloc[0]['heat_ID']
        heat_name = f"{meet_name}: {race_name} Heat {each_heat['heat_info']['heat']}"
        #Check if heat_name exist
        exist_check = f'select exists(select 1 from "Race_Heat_Schedule" where name = \'{heat_name}\');'
        if not engine.execute(exist_check).fetchall()[0][0]:
            qry = f'insert into "Race_Heat_Schedule"("race_ID", "heat_ID", "meet_ID", name, total_skaters, team_race) values ({race_ID}, {heat_ID}, {meet_ID}, \'{heat_name}\', {total_skaters}, {team_bool})'
            engine.execute(qry)
        rhs_ID = engine.execute(f'select "rhs_ID" from "Race_Heat_Schedule" where name = \'{heat_name}\';').fetchall()[0][0]
        #print(rhs_ID)
        for heat_skater in each_heat['skaters']:
            #Create Race_Heat_Schedule_Detail
            if not team_bool:
                st_ID = 'null'
            skater_ID = skater[skater['club_member_number'] == int(heat_skater['skater_num'])].iloc[0]['skater_ID']
            lane_ID = lane[lane['name'] == heat_skater['lane_num']].iloc[0]['lane_ID']
            exist_check = f'select exists(select 1 from "Race_Heat_Schedule_Detail" where "rhs_ID" = \'{rhs_ID}\' and "skater_ID" = \'{skater_ID}\');'
            if not engine.execute(exist_check).fetchall()[0][0]:
                qry = f'insert into "Race_Heat_Schedule_Detail"("rhs_ID", "st_ID", "skater_ID", "lane_ID") values ({rhs_ID}, {st_ID}, {skater_ID}, {lane_ID})'
                engine.execute(qry)
            exist_check = f'select exists(select 1 from "Meet_Skater" where "meet_ID" = \'{meet_ID}\' and "skater_ID" = \'{skater_ID}\');'
            if not engine.execute(exist_check).fetchall()[0][0]:
                gender_ID = skater[skater['skater_ID']==skater_ID].iloc[0]['gender_ID']
                age = find_skating_age(skater[skater['skater_ID']==skater_ID].iloc[0]['dob'])
                division_ID = division[(division['min_age'] <= age) & (division['max_age'] >= age)].iloc[0]['division_ID']
                qry = f'insert into "Meet_Skater"("meet_ID", "skater_ID", "division_ID", "gender_ID") values ({meet_ID}, {skater_ID}, {division_ID}, {gender_ID})'
                engine.execute(qry)

            #print(skater_ID)
        create_race_division_result(meet_ID, race_ID)

# %%
def import_schedule(schedule_path: str) -> dict:
    race_heat_schedules = {}
    heats = get_heat_schedule(schedule_path)
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
        race_heat_schedules[f'race{idx}'] = {'heat_info': heat_info, 'skaters': heat_skaters}
    create_race_heat_schedule_detail(race_heat_schedules)

# %%
def create_race_heat_result(result_file: str) -> int:
    with open(result_file, 'r') as result_file:
        lines = result_file.readlines()
    race_heat_schedule_name = f"{lines[0][:-1]} {lines[1].split(',')[0]}"
    rhs_ID = race_heat_schedule[race_heat_schedule['name'] == race_heat_schedule_name].iloc[0]['rhs_ID']
    timestamp = lines[1].split('  ')[1][:-1]
    timestamp = pd.to_datetime(timestamp).strftime('%H:%M:%S')
    #print(timestamp)
    exist_check = f'select exists(select 1 from "Race_Heat_Result" where "rhs_ID" = \'{rhs_ID}\');'
    if not engine.execute(exist_check).fetchall()[0][0]:
        qry = f'insert into "Race_Heat_Result"("rhs_ID", race_timestamp) values ({rhs_ID}, \'{timestamp}\')'
        engine.execute(qry)
    rhr_ID = engine.execute(f'select "rhr_ID" from "Race_Heat_Result" where "rhs_ID" = \'{rhs_ID}\';').fetchall()[0][0]
    return rhr_ID

# %%
def create_race_heat_result_detail(result_file: str) -> None:
    rhr_ID = create_race_heat_result(result_file)
    COLUMN_NAME = ['rank', 'club_member_number', 'lane', 'name', 'team', 'photo_time']
    result_data = pd.read_csv(result_file, skiprows=2, names=COLUMN_NAME, index_col=None)
    for each_result in result_data.iterrows():
        rank = each_result[1]['rank']
        if rank == 'dnf':
            status_ID = 1
            rank = 0
            photo_time = timedelta(seconds=9999)
            photo_time_in_seconds = 9999
        else:
            status_ID = 2
            photo_time = timedelta(seconds=each_result[1]['photo_time'])
            photo_time_in_seconds = each_result[1]['photo_time']
        st_ID = None
        club_member_number = each_result[1]['club_member_number']
        lane_name = each_result[1]['lane'][1:]
        lane_ID = lane[lane['name']==lane_name].iloc[0]['lane_ID']
        skater_ID = skater[skater['club_member_number']==club_member_number].iloc[0]['skater_ID']
        gender_ID = skater[skater['skater_ID']==skater_ID].iloc[0]['gender_ID']
        age = find_skating_age(skater[skater['skater_ID']==skater_ID].iloc[0]['dob'])
        division_ID = division[(division['min_age'] <= age) & (division['max_age'] >= age)].iloc[0]['division_ID']
        exist_check = f'select exists(select 1 from "Race_Heat_Result_Detail" where "rhr_ID" = \'{rhr_ID}\' and "skater_ID" = \'{skater_ID}\');'
        if not engine.execute(exist_check).fetchall()[0][0]:
            qry = f'insert into "Race_Heat_Result_Detail"("rhr_ID", "skater_ID", "lane_ID", "status_ID", "division_ID", "gender_ID", photo_time, photo_time_in_seconds, rank) values ({rhr_ID}, {skater_ID}, {lane_ID}, {status_ID}, {division_ID}, {gender_ID}, \'{photo_time}\',{photo_time_in_seconds}, {rank})'
            engine.execute(qry)


# %%
# Create a connection to the database
with open('config/config.toml', 'r') as config_value:
    config = toml.load(config_value)
engine = create_engine(f"{config['database']['protocol']}://{config['auth']['username']}:{config['auth']['password']}@{config['server']['host']}:{config['database']['port']}/{config['database']['db']}")

# %%
race_style = pd.read_sql_query('select * from "Race_Style";', con=engine)
club  = pd.read_sql_query('select * from "Club";', con=engine)
skater = pd.read_sql_query('select * from "Skater";', con=engine)
meet = pd.read_sql_query('select * from "Meet";', con=engine)
race = pd.read_sql_query('select * from "Race";', con=engine)
lane = pd.read_sql_query('select * from "Lane";', con=engine)
heat = pd.read_sql_query('select * from "Heat";', con=engine)
division = pd.read_sql_query('select * from "Division";', con=engine)
gender = pd.read_sql_query('select * from "Gender";', con=engine)
import_schedule('./csv/schedule-official.csv')
race_heat_schedule = pd.read_sql_query('select * from "Race_Heat_Schedule";', con=engine)

# %%
# result_file = './csv/result.csv'
# create_race_heat_result_detail(result_file)

# result_file = './csv/result2.csv'
# create_race_heat_result_detail(result_file)
# result_file = './csv/result3.csv'
# create_race_heat_result_detail(result_file)

# %%
