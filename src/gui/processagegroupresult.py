import tkinter as tk
from tkinter import ttk
from sqlalchemy import and_

from skate import utils
from skate.model import *

class ProcessAgeGroupResultLayout(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):

        comp_text = tk.StringVar()

        self.title_label = tk.Label(self, text='Process Age Group Result', font=('helvetica', 24))
        self.title_label.grid(column=0, row=0)

        self.status_text = tk.Text(self, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.controller.insert_text(self.status_text, 'Ready to process imported results for event')
        

        self.comp_frame = ttk.Frame(self)
        self.comp_frame.grid(column=0, row=2, sticky='nsew')


        self.select_comp_label = tk.Label(self.comp_frame,text='select the competition')
        self.select_comp_label.grid(column=0, row=2, sticky='nsew')

        self.comp_combobox = ttk.Combobox(self.comp_frame, textvariable=comp_text)
        self.comp_combobox['values'] = [row.name for row in self.controller.competitions]
        # self.comp_combobox['values'] = self.competition['name'].to_list()
        self.comp_combobox.grid(column=1, row=2, sticky='nsew')
        comp_text.set('select competition')
        # self.comp_combobox['values'] = self.competition['name'].to_list()

        self.comp_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_competition)
        self.comp_combobox_button.grid(column=2, row=2, sticky='nsew')
        
        
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=5, sticky='nsew')

        #adding submit / export / clear / close buttons
        self.button_submit = ttk.Button(self.button_frame, text='Submit', command=lambda: self.process_results(self.status_text))
        self.button_submit.grid(column=0, row=5, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='Clear', command=lambda: self.controller.clear_selection(self.status_text))
        self.button_clear.grid(column=1, row=5, sticky='nsew')
    
        self.button_main = ttk.Button(self.button_frame, text='Main', command=lambda: self.controller.show_frame("MainScreenLayout"))
        self.button_main.grid(column=2, row=5, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='Close', command=self.controller.destroy)
        self.button_close.grid(column=3, row=5, sticky='nsew')

    def clear_all(self):
        self.controller.clear_all()
        self.controller.insert_text(self.status_text, 'Ready to process imported results for event')

    def process_results(self, text_box):
        #create_race_age_group_result
        #create_race_age_group_result_detail
        #rank_race_age_group_result
        
        utils.create_race_age_group_result(self.controller.competition_id, self.controller.event, self.controller.engine)
        # races = pd.read_sql_query(f'select distinct race_id from race_heat_schedule where competition_id = {self.competition_id} and event = {self.event};', self.engine)
        races = self.controller.session.query(self.controller.RHS.race_id).where(and_(self.controller.RHS.competition_id==self.controller.competition_id, self.controller.RHS.event==self.controller.event)).distinct().all()
        print(races)
        for race in races:
            # race_id = each_race.iloc[0]
            utils.create_race_age_group_result_detail(self.controller.competition_id, self.controller.event, race.race_id, self.controller.engine)
        utils.rank_race_age_group_result(self.controller.competition_id, self.controller.event, self.controller.engine)
        msg = f'Event {self.controller.event} results have been processed for {self.controller.competition_name}'
        self.controller.insert_text(text_box, msg)
    
    def select_competition(self):  
        self.controller.competition_name =  self.comp_combobox.get()
        #print(self.controller.competition_name)
        if self.controller.competition_name is not None:
            # print(self.competition)
            # self.competition_id = self.competition[self.competition['name']==self.controller.competition_name].iloc[0]['id']
            # print(self.competition_id)
            self.controller.competition_id = self.controller.session.query(self.controller.Competition).where(self.controller.Competition.name==self.controller.competition_name).first().id
        
            # event_race = pd.read_sql_query(f'select distinct event from race_heat_schedule where competition_id = {self.competition_id};', self.engine)
            event_race = self.controller.session.query(self.controller.RHS.event).where(self.controller.RHS.competition_id==self.controller.competition_id).distinct().all()
            event_text = tk.StringVar()

            # print(event_race)


            self.event_frame = ttk.Frame(self)
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
            self.controller.insert_text(self.status_text, msg)

    def select_event(self):
        self.controller.event = self.event_combobox.get()

