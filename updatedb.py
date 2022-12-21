from sqlalchemy import update, create_engine, MetaData
from sqlalchemy_utils import database_exists
import toml
import pandas as pd

from initial_sql import create_db

division_class_db = pd.read_csv('./db/division_class.csv')
#print(class_db)
country_db = pd.read_csv('./db/country.csv')
division_db = pd.read_csv('./db/Divisions.csv')
heat_db = pd.read_csv('./db/heat.csv')
gender_db = pd.read_csv('./db/gender.csv')
lane_db = pd.read_csv('./db/lane.csv')
race_style_db = pd.read_csv('./db/race_style.csv')
race_db = pd.read_csv('./db/race.csv')
state_db = pd.read_csv('./db/state.csv')
skater_db = pd.read_excel('./db/PSSC member profile for 2022_2023.xlsx')
skater_db['dob'] = skater_db.apply(lambda row: row['MM/DD'].replace(year=row['YYYY']), axis=1)
skater_db['club_member_number'] = skater_db.apply(lambda row: row['pssc_num'] if row['pssc_num'] else 0, axis=1)
skater_db['ngb_member_number'] = skater_db['uss_num']
skater_db['gender_ID'] = skater_db.apply(lambda row: 1 if row['gender'] == 'M' else 2, axis=1)
skater_db['club_ID'] = 1
skater_db['active'] = True
skater_db = skater_db.drop(columns=['MM/DD', 'YYYY', 'uss_num', 'pssc_num', 'gender', 'guest_num'])
club_db = pd.read_csv('./db/club.csv')


with open('config/config.toml', 'r') as config_value:
    config = toml.load(config_value)
engine = create_engine(f"{config['database']['protocol']}://{config['auth']['username']}:{config['auth']['password']}@{config['server']['host']}:{config['database']['port']}/{config['database']['db']}")
# if not database_exists(engine.url):
#     create_db()

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


