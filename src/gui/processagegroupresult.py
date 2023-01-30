import tkinter as tk
from tkinter import ttk
import pandas as pd
from sqlalchemy.orm import aliased
from sqlalchemy import and_

from .baselayer import BaseLayout
from skate import utils
from skate.model import *

AG = aliased(Age_Group)
AGC = aliased(Age_Group_Class)

CS = aliased(Competition_Skater)
CAGR = aliased(Competition_Age_Group_Result)
CAGRD = aliased(Competition_Age_Group_Result_Detail)

RHS = aliased(Race_Heat_Schedule)
RHR = aliased(Race_Heat_Result)
RHRD = aliased(Race_Heat_Result_Detail)
RAGR = aliased(Race_Age_Group_Result)
RHSD = aliased(Race_Heat_Schedule_Detail)
RAGRD = aliased(Race_Age_Group_Result_Detail)
RS = aliased(Race_Style)

class ProcessAgeGroupResultLayout(BaseLayout):
    def __init__(self, root, main_frame, engine):
        super().__init__(root, main_frame, engine)
        self.create_widgets()
        self.competition_name = None
        

    def create_widgets(self):

        self.clear_all()
        self.clear()

        comp_text = tk.StringVar()

        self.title_label = tk.Label(self.main_frame, text='Process Age Group Result', font=('helvetica', 24))
        self.title_label.grid(column=0, row=0)

        self.status_text = tk.Text(self.main_frame, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.insert_text('status_text', 'Ready to process imported results for event')
        

        self.comp_frame = ttk.Frame(self.main_frame)
        self.comp_frame.grid(column=0, row=2, sticky='nsew')


        self.select_comp_label = tk.Label(self.comp_frame,text='select the competition')
        self.select_comp_label.grid(column=0, row=2, sticky='nsew')

        self.comp_combobox = ttk.Combobox(self.comp_frame, textvariable=comp_text)
        self.comp_combobox['values'] = [row.name for row in self.competition]
        # self.comp_combobox['values'] = self.competition['name'].to_list()
        self.comp_combobox.grid(column=1, row=2, sticky='nsew')
        comp_text.set('select competition')
        # self.comp_combobox['values'] = self.competition['name'].to_list()

        self.comp_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_competition)
        self.comp_combobox_button.grid(column=2, row=2, sticky='nsew')
        
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(column=0, row=5, sticky='nsew')

        #adding submit / export / clear / close buttons
        self.button_submit = ttk.Button(self.button_frame, text='submit', command=self.process_results)
        self.button_submit.grid(column=0, row=5, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='clear', command=self.clear_selection('status_text'))
        self.button_clear.grid(column=1, row=5, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='close', command=self.root.destroy)
        self.button_close.grid(column=2, row=5, sticky='nsew')

    def process_results(self):
        #create_race_age_group_result
        #create_race_age_group_result_detail
        #rank_race_age_group_result
        
        utils.create_race_age_group_result(self.competition_id, self.event, self.engine)
        # races = pd.read_sql_query(f'select distinct race_id from race_heat_schedule where competition_id = {self.competition_id} and event = {self.event};', self.engine)
        races = self.session.query(RHS.race_id).where(and_(RHS.competition_id==self.competition_id, RHS.event==self.event)).distinct().all()
        print(races)
        for race in races:
            # race_id = each_race.iloc[0]
            utils.create_race_age_group_result_detail(self.competition_id, self.event, race.race_id, self.engine)
        utils.rank_race_age_group_result(self.competition_id, self.event, self.engine)
        msg = f'Event {self.event} results have been processed for {self.competition_name}'
        self.insert_text('status_text', msg)
    
    def select_competition(self):  
        self.competition_name =  self.comp_combobox.get()
        #print(self.competition_name)
        if self.competition_name is not None:
            # print(self.competition)
            # self.competition_id = self.competition[self.competition['name']==self.competition_name].iloc[0]['id']
            # print(self.competition_id)
            self.competition_id = self.session.query(Competition).where(Competition.name==self.competition_name).first().id
        
            # event_race = pd.read_sql_query(f'select distinct event from race_heat_schedule where competition_id = {self.competition_id};', self.engine)
            event_race = self.session.query(RHS.event).where(RHS.competition_id==self.competition_id).distinct().all()
            event_text = tk.StringVar()

            # print(event_race)


            self.event_frame = ttk.Frame(self.main_frame)
            self.event_frame.grid(column=0, row=3, sticky='nsew')


            self.select_event_label = tk.Label(self.comp_frame,text='select the event')
            self.select_event_label.grid(column=0, row=3, sticky='nsew')

            self.event_combobox = ttk.Combobox(self.comp_frame, textvariable=event_text)
            # values = event_race['event'].to_list() #event value
            values = [row.event for row in event_race]
            values.sort()
            self.event_combobox['values'] = values
            values = None
            self.event_combobox.grid(column=1, row=3, sticky='nsew')
            event_text.set('select competition')

            self.event_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_event)
            self.event_combobox_button.grid(column=2, row=3, sticky='nsew')
        else:
            msg = 'please select the competition.'
            self.insert_text('status_text', msg)

    def select_event(self):
        self.event = self.event_combobox.get()

