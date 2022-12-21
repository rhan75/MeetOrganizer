import pandas as pd
import json
import sqlite3
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# import sqlalchemy
# from database import get_db_connection

# DB_LOCATION = 'db/database.db'


'''
get_race_info: return a dictionary that contains:
    Race Date: datetime
    Race Distance: int
    Race Timestamp: time
    Heat: str
    date / distance / time / heat
'''
def get_race_info(race_result_csv: str) -> dict:
    info = {}
    event_name = race_result_csv.split('\n')[0] #First row contains event name and distance
    event_detail = race_result_csv.split('\n')[1] #second row contains heat, date, timestamp
    info['date'] = f"{(event_detail.split(' ')[4]).strip()}-{event_name.split(' ')[0]}"
    info['distance'] = event_name.split(' ')[1]
    info['timestamp'] = f"{event_detail.split(' ')[6]} {(event_detail.split(' ')[7]).rstrip()}"
    info['heat'] = event_detail.split(',')[0]
    #print(details)
    return info

def find_skating_age(dob: datetime) -> int:
    current_time = datetime.now()
    if current_time.month > 7:
        skating_year = current_time.year
    else:
        skating_year = current_time.year - 1
    skating_age_date = datetime(skating_year, 6, 30)
    return int(int((skating_age_date - dob).days) / 365.2425)


def get_skater_info(membership_number) -> dict:
    #query using membership_number
    qry = f'select skater_ID, dob, club_ID from Skater where member_number = {membership_number}'
    #send qry and catch the result
    dob = 'something'
    skater_age = get_skater_age(dob=dob)
    # Using skater age, determine division
    division_qry = f'select division_ID from Division where min_age = {skater_age} or max_age = {skater_age}'
    cursor 
    if  
    class_qry = f''
    skater_info = {}
    skater_ID = 1 # Get skater_ID from skater table
    division_ID = 1 # Get skater's division using dob
    class_ID = 1 # Get skater's class within division using dob
    seed_time = timedelta(seconds=58.56) # Get seed_time from skater table
    skater_info['skater_ID'] = skater_ID
    skater_info['division_ID'] = division_ID
    skater_info['class_ID'] = class_ID
    skater_info['seed'] = seed_time
    return skater_info

def 

'''
Take race_rasult and race_info and update race_details
'''
# race_result comes from SprintTimer csv
# race_info comes from get_race_info

def update_heat_result(race_result: pd.DataFrame) -> None:
    race_info = get_race_info(race_result) # event date / distance / timestamp / heat
    skater_info = get_skater_info()
    race_details = []
    # Need skater name / result / lane / time / lane from CSV
    # Iterate each row and get skater name / lane / result time
    # Using skater name, get skater_ID, division_ID, class_ID, seed get_skater_info
    # Using lane, get lane_ID from Lane table
    # 
    # Using race_info to get date / distance and heat info
    # Using date to get event_ID, distance to get race_ID, heat to get heat_ID
    # Using event_ID and race_ID to get ed_ID
    # Using ed_ID, heat_ID, division_ID, class_ID, rounte_ID to get result_ID
    # Create a result_detail record using result_ID, skater_ID, lane_ID, race_time 
    # Update SQL with created result_detail record
    for ind, row in race_result.iterrows():
        name = row[3]
        first_name = name.split(' ')[0]
        last_name = name.split(' ')[1]
        if row[0] == 'dnf':
            heat_ranking = None
            race_time = None
        else:
            heat_ranking = row[0]
            race_time = row[5]
        membership = row[1]
        lane = row[2]
        club = row[4]
        # Check if skater # and name matches? 

        
        #print(race_info['distance'])
        #race_detail = {}
        #skater_num = row['Skater Number']
        skater_idx = skaters.index[skaters['skater_id']==row['Skater Number']].tolist()
        event_idx = events.index[events['Date']==race_info['date']].tolist()
        race_idx = races.index[races['distance']==race_info['distance']].tolist()
        print(races)
        print(race_idx)
        #print(skater_num)#, idx)
        #skater_info = skaters.iloc[skater_idx[0]].values
        #event_info = events.iloc[idx[0]].values
        race_detail['skater_id'] = skater_idx[0]
        race_detail['event_id'] = event_idx[0]
        #race_detail['race_id'] = race_idx[0]
        print(race_result['time'])
        race_detail['Time'] = race_result['Time']
        race_details.append(race_detail)
    return race_details