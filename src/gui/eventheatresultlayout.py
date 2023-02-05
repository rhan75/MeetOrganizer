import tkinter as tk
from tkinter import ttk

from skate import reports
from skate import utils
from skate.model import *


class GenerateEventHeatResultLayout(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()


    def create_widgets(self):

        comp_text = tk.StringVar()

        self.title_label = tk.Label(self, text='Generate Heat Result for Event', font=('Arial', 24))
        self.title_label.grid(column=0, row=0, sticky='nsew')

        self.status_text = tk.Text(self, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.controller.insert_text(self.status_text, 'Ready to generate event results for age groups')
        

        self.comp_frame = ttk.Frame(self)
        self.comp_frame.grid(column=0, row=2, sticky='nsew')


        self.select_comp_label = tk.Label(self.comp_frame,text='select the competition')
        self.select_comp_label.grid(column=0, row=2, sticky='nsew')

        self.comp_combobox = ttk.Combobox(self.comp_frame, textvariable=comp_text)
        # self.comp_combobox['values'] = self.competition['name'].to_list()
        self.comp_combobox.grid(column=1, row=2, sticky='nsew')
        comp_text.set('select competition')
        self.comp_combobox['values'] = [row.name for row in self.controller.competitions]
        # self.comp_combobox['values'] = self.competition['name'].to_list()

        self.comp_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_competition)
        self.comp_combobox_button.grid(column=2, row=2, sticky='nsew')
        
        
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=5, sticky='nsew')

        #adding submit / export / clear / close buttons
        self.button_submit = ttk.Button(self.button_frame, text='submit', command=self.generate_report)
        self.button_submit.grid(column=0, row=5, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='clear', command=self.clear_all)
        self.button_clear.grid(column=1, row=5, sticky='nsew')

        self.button_main = ttk.Button(self.button_frame, text='Main', command=lambda: self.controller.show_frame("MainScreenLayout"))
        self.button_main.grid(column=2, row=5, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='close', command=self.controller.destroy)
        self.button_close.grid(column=3, row=5, sticky='nsew')


    def clear_all(self):
        self.controller.clear_all()
        self.controller.insert_text(self.status_text, 'Ready to generate event results for age groups')

    def generate_report(self):
        reports.generate_race_heat_report(self.controller.competition_id, self.controller.event, self.controller.directory, self.controller.engine)
        # self.competition_name = self.competition[self.competition['id']==self.competition_id].iloc[0]['name']
        msg = f'Report for event {self.controller.event} from {self.controller.competition_name} has been generated in {self.controller.directory}'
        self.controller.insert_text(self.status_text, msg)
    
    def select_competition(self):  
        self.controller.competition_name =  self.comp_combobox.get()
        #print(self.competition_name)
        if self.controller.competition_name is not None:
            self.controller.competition_id = utils.get_object_info(self.controller.session, Competition, name=self.controller.competition_name)[0].id
        
            evtrace = utils.get_object_info(self.controller.session, Race_Heat_Schedule, competition_id=self.controller.competition_id)
            event_race = set(row.event for row in evtrace)
            # event_race = set(event_race)
            event_text = tk.StringVar()


            self.event_frame = ttk.Frame(self)
            self.event_frame.grid(column=0, row=3, sticky='nsew')


            self.select_event_label = tk.Label(self.comp_frame,text='select the event')
            self.select_event_label.grid(column=0, row=3, sticky='nsew')

            self.event_combobox = ttk.Combobox(self.comp_frame, textvariable=event_text)
            # values = event_race['event'].to_list() #event value
            values = [row for row in event_race]
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
        self.controller.event = self.event_combobox.get()

        self.report_frame = ttk.Frame(self)
        self.report_frame.grid(column=0, row=4, sticky='nsew')


        self.report_label = tk.Label(self.report_frame,text='select the path')
        self.report_label.grid(column=0, row=4, sticky='nsew')

        self.report_text = tk.Text(self.report_frame,state='disabled',height=1)
        self.report_text.grid(column=1, row=4, sticky='nsew')
        # self.schedule_text.pack(side='left')
        self.browse_button = ttk.Button(self.report_frame,text='browse', command=lambda: self.controller.select_folder(self.report_text))
        self.browse_button.grid(column=2, row=4, sticky='nsew')
