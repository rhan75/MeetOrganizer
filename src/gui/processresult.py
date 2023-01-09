import tkinter as tk
from tkinter import ttk
import pandas as pd

from .baselayer import BaseLayout
from skate import utils

class ProcessResultLayout(BaseLayout):
    def __init__(self, root, main_frame, engine):
        super().__init__(root, main_frame, engine)
        self.create_widgets()

    def create_widgets(self):

        self.clear_all()

        comp_text = tk.StringVar()

        self.title_label = tk.Label(self.main_frame, text='Process Result', font=('helvetica', 24))
        self.title_label.grid(column=0, row=0)

        self.status_text = tk.Text(self.main_frame, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.insert_text('status_text', 'Ready to process imported results for event')
        

        self.comp_frame = ttk.Frame(self.main_frame)
        self.comp_frame.grid(column=0, row=2, sticky='nsew')


        self.select_comp_label = tk.Label(self.comp_frame,text='select the competition')
        self.select_comp_label.grid(column=0, row=2, sticky='nsew')

        self.comp_combobox = ttk.Combobox(self.comp_frame, textvariable=comp_text)
        # self.comp_combobox['values'] = self.meet['name'].to_list()
        self.comp_combobox.grid(column=1, row=2, sticky='nsew')
        comp_text.set('select competition')
        self.comp_combobox['values'] = self.meet['name'].to_list()

        self.comp_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_competition)
        self.comp_combobox_button.grid(column=3, row=2, sticky='nsew')
        
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(column=0, row=5, sticky='nsew')

        #adding submit / export / clear / close buttons
        self.button_submit = ttk.Button(self.button_frame, text='submit', command=self.process_results)
        self.button_submit.grid(column=0, row=5, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='clear', command=self.clear_selection('status_text'))
        self.button_clear.grid(column=2, row=5, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='close', command=self.root.destroy)
        self.button_close.grid(column=4, row=5, sticky='nsew')

    def process_results(self):
        #create_race_division_result
        #create_race_division_result_detail
        #rank_race_division_result
        
        utils.create_race_division_result(self.meet_ID, self.event, self.engine)
        races = pd.read_sql_query(f'select distinct "race_ID" from "Race_Heat_Schedule" where "meet_ID" = {self.meet_ID} and event = {self.event};', self.engine)
        for idx, each_race in races.iterrows():
            race_ID = each_race.iloc[0]
            utils.create_race_division_result_detail(self.meet_ID, race_ID, self.engine)
        utils.rank_race_division_result(self.meet_ID, self.event, self.engine)
        msg = f'Event {self.event} results have been processed for {self.meet_name}'
        self.insert_text('status_text', msg)
    
    def select_competition(self):  
        self.meet_name =  self.comp_combobox.get()
        #print(self.meet_name)
        if self.meet_name is not None:
            self.meet_ID = self.meet[self.meet['name']==self.meet_name]['meet_ID'][0]
        
            event_race = pd.read_sql_query(f'select distinct race.name, race."race_ID", event from "Race_Heat_Schedule" as rhs left join "Race" as race on rhs."race_ID" = race."race_ID" where "meet_ID" = {self.meet_ID};', self.engine)
            event_text = tk.StringVar()


            self.event_frame = ttk.Frame(self.main_frame)
            self.event_frame.grid(column=0, row=3, sticky='nsew')


            self.select_event_label = tk.Label(self.comp_frame,text='select the event')
            self.select_event_label.grid(column=0, row=3, sticky='nsew')

            self.event_combobox = ttk.Combobox(self.comp_frame, textvariable=event_text)
            values = event_race['event'].to_list() #event value
            values.sort()
            self.event_combobox['values'] = values
            values = None
            self.event_combobox.grid(column=1, row=3, sticky='nsew')
            event_text.set('select competition')

            self.event_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_event)
            self.event_combobox_button.grid(column=4, row=3, sticky='nsew')
        else:
            msg = 'please select the competition.'
            self.insert_text('status_text', msg)

    def select_event(self):
        self.event = self.event_combobox.get()

