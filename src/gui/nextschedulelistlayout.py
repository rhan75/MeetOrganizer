import tkinter as tk
from tkinter import ttk
import pandas as pd

from .baselayer import BaseLayout
from skate import reports

class GenerateNextScheduleListLayout(BaseLayout):
    def __init__(self, root, main_frame, engine):
        super().__init__(root, main_frame, engine)
        self.create_widgets()
        self.low_division = None
        self.high_division = None
        self.division_range = None

    def create_widgets(self):

        self.clear_all()
        self.clear()

        comp_text = tk.StringVar()

        self.title_label = tk.Label(self.main_frame, text='Generate Next Schedule List', font=('helvetica', 24))
        self.title_label.grid(column=0, row=0, sticky='nsew')

        self.status_text = tk.Text(self.main_frame, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.insert_text('status_text', 'Ready to generate event results for divisions')
        

        self.comp_frame = ttk.Frame(self.main_frame)
        self.comp_frame.grid(column=0, row=2, sticky='nsew')


        self.select_comp_label = tk.Label(self.comp_frame,text='select the competition')
        self.select_comp_label.grid(column=0, row=2, sticky='nsew')

        self.comp_combobox = ttk.Combobox(self.comp_frame, textvariable=comp_text)
        
        self.comp_combobox.grid(column=1, row=2, sticky='nsew')
        comp_text.set('select competition')
        self.comp_combobox['values'] = self.meet['name'].to_list()

        self.comp_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_competition)
        self.comp_combobox_button.grid(column=2, row=2, sticky='nsew')
        
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(column=0, row=6, sticky='nsew')

        #adding submit / export / clear / close buttons
        self.button_submit = ttk.Button(self.button_frame, text='submit', command=self.generate_report)
        self.button_submit.grid(column=0, row=6, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='clear', command=self.reload_frame)
        self.button_clear.grid(column=1, row=6, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='close', command=self.root.destroy)
        self.button_close.grid(column=2, row=6, sticky='nsew')

    def reload_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy
        self.create_widgets()

    def generate_report(self):
        reports.generate_event_schedule_list_report(self.meet_ID, self.event, self.folder_name, self.division_range, self.engine)
        self.meet_name = self.meet[self.meet['meet_ID']==self.meet_ID]['name'][0]
        msg = f'Result for event {self.event} from {self.meet_name} has been generated in {self.folder_name}'
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
            self.event_combobox.grid(column=1, row=3, sticky='nswe')
            event_text.set('select competition')

            self.event_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_event)
            self.event_combobox_button.grid(column=2, row=3, sticky='w')
        else:
            msg = 'please select the competition.'
            self.insert_text('status_text', msg)

    def select_event(self):
        self.event = self.event_combobox.get()

        division = pd.read_sql_query('select "division_ID", name from "Division";', con=self.engine)
        
        self.division_frame = ttk.Frame(self.main_frame)
        self.division_frame.grid(column=0, row=4, sticky='nsew')


        self.division_label = tk.Label(self.division_frame,text='select the range of age groups')
        self.division_label.grid(column=0, row=4, sticky='nsew')

        division_low_text = tk.StringVar()
        division_high_text = tk.StringVar()

        self.division_low_combobox = ttk.Combobox(self.division_frame, textvariable=division_low_text )
        self.division_low_combobox.grid(column=1, row=4, sticky='nsew')
        self.division_low_combobox['values'] = division['name'].to_list()
        division_low_text.set('Select the lower division')

        self.division_high_combobox = ttk.Combobox(self.division_frame, textvariable=division_high_text )
        self.division_high_combobox.grid(column=2, row=4, sticky='nsew')
        self.division_high_combobox['values'] = division['name'].to_list()
        division_high_text.set('Select the higher division')
                
        self.division_combobox_button = ttk.Button(self.division_frame,text='select', command=self.select_division)
        self.division_combobox_button.grid(column=3, row=4, sticky='nsew')

    def select_division(self):
        division = pd.read_sql_query('select "division_ID", name from "Division";', con=self.engine)
        low = division[division['name']== self.division_low_combobox.get()].head(1)
        high = division[division['name']== self.division_high_combobox.get()].head(1)
        self.low_division = low['division_ID'].iloc[0]
        self.high_division = high['division_ID'].iloc[0]
        self.division_range = {'low_division': {'name':self.division_low_combobox.get(), 'division_ID':self.low_division}, 'high_division': {'name':self.division_high_combobox.get(), 'division_ID':self.high_division}}
        # print(self.low_division, self.high_division)
        # print(division[division['name']==low_div_name]['division_ID'][0])
        # self.low_division = division[division['name']==low_div_name]['division_ID'].iloc[0]
        # self.high_division = division[division['name']==high_div_name]['division_ID'].iloc[0]
        
        self.report_frame = ttk.Frame(self.main_frame)
        self.report_frame.grid(column=0, row=5, sticky='nsew')


        self.report_label = tk.Label(self.report_frame,text='select the path')
        self.report_label.grid(column=0, row=5, sticky='nsew')

        self.report_text = tk.Text(self.report_frame,state='disabled',height=1)
        self.report_text.grid(column=1, row=5, sticky='nsew')
        # self.schedule_text.pack(side='left')
        self.browse_button = ttk.Button(self.report_frame,text='browse', command=lambda: self.select_folder('report_text'))
        self.browse_button.grid(column=2, row=5, sticky='nsew')