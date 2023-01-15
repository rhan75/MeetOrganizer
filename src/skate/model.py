#import sqlite3
from sqlalchemy import create_engine, Float, Table, Column, Integer, String, MetaData, Date, Time, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy_utils import database_exists, create_database

meta = MetaData()
Base = declarative_base()

class Score(Base):
    __tablename__ = 'score'

    id = Column(Integer, primary_key = True)
    rank = Column(Integer)
    point = Column(Integer)

    def __repr__(self) -> str:
        return f'Score(id={self.id}, rank={self.rank}, point={self.point}'

class Skater(Base):
    __tablename__ = 'skater'

    id = Column(Integer, primary_key = True)
    club_id = Column(Integer, ForeignKey('club.id'), nullable=True)
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
    club_member_number = Column(Integer)
    first_name = Column(String(20))
    last_name = Column(String(20))
    dob = Column(Date)
    ngb_member_number = Column(Integer)
    ngb_name = Column(String)

    def __repr__(self) -> str:
        return f'Skater(id={self.id}, First Name={self.first_name}, Last Name={self.last_name}'

class Skater_Team(Base):
    __tablename__ = 'skater_team'

    id = Column(Integer, primary_key = True)
    skater1_id = Column(Integer, ForeignKey('skater.id'), nullable=True)
    skater2_id = Column(Integer, ForeignKey('skater.id'), nullable=True)
    skater3_id = Column(Integer, ForeignKey('skater.id'), nullable=True)
    skater4_id = Column(Integer, ForeignKey('skater.id'), nullable=True)
    team_name = Column(String)

    def __repr__(self) -> str:
        return f'Skater_Team(id={self.id}, Team name={self.team_name}'

class Club(Base):
    __tablename__ = 'club'

    id = Column(Integer, primary_key = True)
    us_based = Column(Boolean)
    name = Column(String(50))
    abbreviation = Column(String(10))

    def __repr__(self) -> str:
        return f'Club(id={self.id}, Club Name={self.name}'

class Status(Base):
    __tablename__ = 'status'

    id = Column(Integer, primary_key = True)
    name = Column(String(10))

    def __repr__(self) -> str:
        return f'Status(id={self.id}, Status={self.name}'

class Age_Group(Base):
    __tablename__ = 'age_group'

    id = Column(Integer, primary_key = True)
    name = Column(String(50))
    min_age = Column(Integer)
    max_age = Column(Integer)


    def __repr__(self) -> str:
        return f'Age Group(id={self.id}, Name={self.name} from age {self.min_age} to age {self.max_age}'

class Age_Group_Class(Base):
    __tablename__ = 'age_group_class'

    id = Column(Integer, primary_key = True)
    name = Column(String(1))

    def __repr__(self) -> str:
        return f'Age Group Class(id={self.id}, Name={self.name}'

class Gender(Base):
    __tablename__ = 'gender'

    id = Column(Integer, primary_key = True)
    name = Column(String(10))

    def __repr__(self) -> str:
        return f'Gender(id={self.id}, Name={self.name}'

class Lane(Base):
    __tablename__ = 'lane'

    id = Column(Integer, primary_key = True)
    name = Column(String(5))

    def __repr__(self) -> str:
        return f'Lane(id={self.id}, Name={self.name}'

class Race_Style(Base):
    __tablename__ = 'race_style'

    id = Column(Integer, primary_key = True)
    name = Column(String(15))

    def __repr__(self) -> str:
        return f'Race Style(id={self.id}, Name={self.name}'

class Race(Base):
    __tablename__ = 'race'

    id = Column(Integer, primary_key = True)
    rs_id = Column(Integer, ForeignKey('race_style.id'), nullable=False)
    name = Column(String(15))
    distance = Column(Integer)
    team = Column(Boolean)

    def __repr__(self) -> str:
        return f'Race(id={self.id}, Name={self.name}, Distance={self.distance}, Team Race={self.team}'

class Competition(Base):
    __tablename__ = 'competition'

    id = Column(Integer, primary_key = True)
    name = Column(String(50))
    start_date = Column(Date)
    end_date = Column(Date)

    def __repr__(self) -> str:
        return f'Competition(id={self.id}, Name={self.name}, From {self.start_date}~{self.end_date}'

class Competition_Skater(Base):
    __tablename__ = 'competition_skater'

    id = Column(Integer, primary_key = True)
    compeition_id = Column(Integer, ForeignKey('competition.id'), nullable=False)
    skater_id = Column(Integer, ForeignKey('skater.id'), nullable=False)
    ag_id = Column(Integer, ForeignKey('age_group.id'), nullable=False)
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)

    def __repr__(self) -> str:
        return f'Competition Skater(id={self.id}, Competition={self.compeition_id}, Skater={self.skater_id}'

class Heat(Base):
    __tablename__ = 'heat'

    id = Column(Integer, primary_key = True)
    name = Column(String(15))

    def __repr__(self) -> str:
        return f'Heat(id={self.id}, Name={self.name}'

class Race_Heat_Schedule(Base):
    __tablename__ = 'race_heat_schedule'

    id = Column(Integer, primary_key = True)
    race_id = Column(Integer, ForeignKey('race.id'), nullable=False)
    heat_id = Column(Integer, ForeignKey('heat.id'), nullable=False)
    competition_id = Column(Integer, ForeignKey('competition.id'), nullable=False)
    event = Column(Integer)
    name = Column(String(50))
    total_sakters = Column(Integer)
    team_race = Column(Boolean)

    def __repr__(self) -> str:
        return f'Race_Heat_Schedule(id={self.id}, Name={self.name}, Event={self.event}, Total Skaters={self.total_sakters}'

class Race_Heat_Schedule_Detail(Base):
    __tablename__ = 'race_heat_schedule_detail'

    id = Column(Integer, primary_key = True)
    rhs_id = Column(Integer, ForeignKey('race_heat_schedule.id'), nullable=False)
    st_id = Column(Integer, ForeignKey('skater_team.id'), nullable=True)
    skater_id = Column(Integer, ForeignKey('skater.id'), nullable=True)
    lane_id = Column(Integer, ForeignKey('lane.id'), nullable=False)

    def __repr__(self) -> str:
        return f'Race_Heat_Schedule_Detail(id={self.id})'

class Race_Heat_Result(Base):
    __tablename__ = 'race_heat_result'

    id = Column(Integer, primary_key = True)
    rhs_id = Column(Integer, ForeignKey('race_heat_schedule.id'), nullable=False)
    timestamp = Column(Time)

    def __repr__(self) -> str:
        return f'Race_Heat_Result(id={self.id} started @ {self.race_timestamp}'    


class Race_Heat_Result_Detail(Base):
    __tablename__ = 'race_heat_result_detail'

    id = Column(Integer, primary_key = True)
    rhr_id = Column(Integer, ForeignKey('race_heat_result.id'), nullable=False)
    st_id = Column(Integer, ForeignKey('skater_team.id'), nullable=True)
    skater_id = Column(Integer, ForeignKey('skater.id'), nullable=True)
    lane_id = Column(Integer, ForeignKey('lane.id'), nullable=False)
    status_id = Column(Integer, ForeignKey('status.id'), nullable=False)
    ag_id = Column(Integer, ForeignKey('age_group.id'), nullable=False)
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
    time_type = Column(String)
    time = Column(Time)
    time_in_seconds = Column(Float)
    rank = Column(Integer)

    def __repr__(self) -> str:
        return f'Race_Heat_Result_Detail(id={self.id}), Skater ID={self.skater_id}, Time={self.time}'

class Race_Age_Group_Result(Base):
    __tablename__ = 'race_age_group_result'

    id = Column(Integer, primary_key = True)
    competition_id = Column(Integer, ForeignKey('competition.id'), nullable=False)
    ag_id = Column(Integer, ForeignKey('age_group.id'), nullable=False)
    race_id = Column(Integer, ForeignKey('race.id'), nullable=False)
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
    name = Column(String)

    def __repr__(self) -> str:
        return f'race_age_group_result(id={self.id}), name={self.name}'

class Race_Age_Group_Result_Detail(Base):
    __tablename__ = 'race_age_group_result_detail'

    id = Column(Integer, primary_key = True)
    ragr_id = Column(Integer, ForeignKey('race_age_group_result.id'), nullable=False)
    rhrd_id = Column(Integer, ForeignKey('race_heat_result_detail.id'), nullable=False)
    time_in_seconds = Column(Time)
    rank = Column(Integer)
    score = Column(Integer)

    def __repr__(self) -> str:
        return f'race_age_group_result_detail(id={self.id})'

class Competition_Age_Group_Result(Base):
    __tablename__ = 'competition_age_group_result'

    id = Column(Integer, primary_key = True)
    competition_id = Column(Integer, ForeignKey('competition.id'), nullable=False)
    ag_id = Column(Integer, ForeignKey('age_group.id'), nullable=False)
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
    name = Column(String)

    def __repr__(self) -> str:
        return f'Race_age_group_Result(id={self.id}), name={self.name}'

class Competition_Age_Group_Result_Detail(Base):
    __tablename__ = 'competition_heat_result_detail'

    id = Column(Integer, primary_key = True)
    competition_age_group_result_id = Column(Integer, ForeignKey('competition_age_group_result.id'), nullable=False)
    rhrd_id = Column(Integer, ForeignKey('race_heat_result_detail.id'), nullable=False)
    skater_id = Column(Integer, ForeignKey('skater.id'), nullable=True)
    rank = Column(Integer)
    total_score = Column(Integer)