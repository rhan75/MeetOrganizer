import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.engine.base import Engine
import pandas as pd
from skate.model import *
#from connection import create_connection

class BaseLayout:
    def __init__(self, root, main_frame, engine):
        self.AG = aliased(Age_Group)
        self.AGC = aliased(Age_Group_Class)

        self.CS = aliased(Competition_Skater)
        self.CAGR = aliased(Competition_Age_Group_Result)
        self.CAGRD = aliased(Competition_Age_Group_Result_Detail)

        self.RHS = aliased(Race_Heat_Schedule)
        self.RHR = aliased(Race_Heat_Result)
        self.RHRD = aliased(Race_Heat_Result_Detail)
        self.RAGR = aliased(Race_Age_Group_Result)
        self.RHSD = aliased(Race_Heat_Schedule_Detail)
        self.RAGRD = aliased(Race_Age_Group_Result_Detail)
        self.RS = aliased(Race_Style)
        self.Skater = Skater
        self.Competition = Competition
        self.Race = Race
        self.Heat = Heat
        self.Lane = Lane
        self.Gender = Gender
        self.root = root
        self.main_frame = main_frame
        self.filename = None
        self.result = None
        self.directory = None
        self.competition_id = None
        self.event = None
        self.gender = None
        # self.competition_name = None
        # self.competition = pd.read_sql_query('select id, name from competition;', con=engine)
        
        self.engine = engine
        self.session = None
        self.prep_session(engine)
        self.competition = self.session.query(Competition).all()


    def clear(self):
        # destroy all of the widgets in the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def insert_text(self, textbox, text):
        widget = getattr(self, textbox)
        widget.configure(state='normal')
        widget.delete('1.0', tk.END)
        widget.insert(tk.END, text)
        widget.configure(state='disabled')
    
    def select_file(self, textbox):
        self.filename = askopenfilename()
        self.insert_text(textbox, self.filename)
    
    def clear_all(self):
        self.filename = None
        self.result = None
        self.directory = None
        self.competition_id = None
        self.event = None
        self.gender = None
        self.competition_name = None
        # self.competition = None
        # self.engine = None
    
    def clear_selection(self, textbox: str):
        self.clear_all()
        self.insert_text(textbox, '')

    def select_folder(self, textbox):
        self.folder_name = askdirectory()
        self.insert_text(textbox, self.folder_name)

    def prep_session(self, engine: Engine):
        Session = sessionmaker(bind=engine)
        self.session = Session()