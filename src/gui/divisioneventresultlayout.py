import tkinter as tk
from tkinter import ttk
import pandas as pd

from .baselayer import BaseLayout
from skate import reports

class GenerateDivisionEventResultLayout(BaseLayout):
    def __init__(self, root, main_frame, engine):
        super().__init__(root, main_frame, engine)
        self.create_widgets()

    def create_widgets(self):

        self.clear_all()
        self.clear()

        comp_text = tk.StringVar()

        self.title_label = tk.Label(self.main_frame, text='Generate Division Result for Event', font=('helvetica', 24))
        self.title_label.grid(column=0, row=0, sticky='nsew')

        self.status_text = tk.Text(self.main_frame, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.insert_text('status_text', 'Ready to generate division result for event')
        

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
        self.comp_combobox_button.grid(column=2, row=2, sticky='nsew')
        
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(column=0, row=5, sticky='nsew')

        #adding submit / export / clear / close buttons
        self.button_submit = ttk.Button(self.button_frame, text='submit', command=self.generate_report)
        self.button_submit.grid(column=0, row=5, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='clear', command=self.clear_selection('status_text'))
        self.button_clear.grid(column=1, row=5, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='close', command=self.root.destroy)
        self.button_close.grid(column=2, row=5, sticky='nsew')

    def generate_report(self):
        reports.generate_division_report(self.competition_id, self.event, self.folder_name, self.engine)
        msg = f'Age Group Report for event {self.event} from {self.competition_name} has been generated in {self.folder_name}'
        self.insert_text('status_text', msg)
    
    def select_competition(self):  
        self.competition_name =  self.comp_combobox.get()
        #print(self.competition_name)
        if self.competition_name is not None:
            self.competition_id = self.meet[self.meet['name']==self.competition_name]['competition_id'][0]
        
            event_race = pd.read_sql_query(f'select distinct race.name, race.race_id, event from race_heat_schedule as rhs left join race as race on rhs.race_id = race.race_id where competition_id = {self.competition_id};', self.engine)
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
            self.event_combobox_button.grid(column=2, row=3, sticky='nsew')
        else:
            msg = 'please select the competition.'
            self.insert_text('status_text', msg)

    def select_event(self):
        self.event = self.event_combobox.get()

        self.report_frame = ttk.Frame(self.main_frame)
        self.report_frame.grid(column=0, row=4, sticky='nsew')


        self.report_label = tk.Label(self.report_frame,text='select the path')
        self.report_label.grid(column=0, row=4, sticky='nsew')

        self.report_text = tk.Text(self.report_frame,state='disabled',height=1)
        self.report_text.grid(column=1, row=4, sticky='nsew')
        # self.schedule_text.pack(side='left')
        self.browse_button = ttk.Button(self.report_frame,text='browse', command=lambda: self.select_folder('report_text'))
        self.browse_button.grid(column=2, row=4, sticky='nsew')
