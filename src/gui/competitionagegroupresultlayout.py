import tkinter as tk
from tkinter import ttk

from skate import reports
from skate import utils
from models.model import *

class GenerateCompetitionAgeGroupResultLayout(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        comp_text = tk.StringVar()

        self.title_label = tk.Label(self, text='Generate Combined Result for the Competition', font=('Arial', 24))
        self.title_label.grid(column=0, row=0)

        self.status_text = tk.Text(self, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.controller.insert_text(self.status_text, 'Ready to generate combined result for the competition')
        

        self.comp_frame = ttk.Frame(self)
        self.comp_frame.grid(column=0, row=2, sticky='nsew')


        self.select_comp_label = tk.Label(self.comp_frame,text='select the competition')
        self.select_comp_label.grid(column=0, row=2, sticky='nsew')

        self.comp_combobox = ttk.Combobox(self.comp_frame, textvariable=comp_text)
        # self.comp_combobox['values'] = self.competition['name'].to_list()
        self.comp_combobox.grid(column=1, row=2, sticky='nsew')
        comp_text.set('select competition')
        self.comp_combobox['values'] = [row.name for row in self.controller.competitions]

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
        self.controller.insert_text(self.status_text, 'Ready to generate combined result for the competition')

    def generate_report(self):
        utils.create_competition_age_group_result(self.controller.competition_id, self.controller.engine)
        utils.create_competition_age_group_result_detail(self.controller.competition_id, self.controller.engine)
        utils.rank_competition_age_group_result(self.controller.competition_id, self.controller.engine)
        

        reports.generate_competition_age_group_report(self.controller.competition_id, self.controller.directory, self.controller.engine)
        msg = f'The Combined Report for {self.controller.competition_name} has been generated in {self.controller.directory}'
        self.controller.insert_text(self.status_text, msg)
    
    def select_competition(self):  
        self.controller.competition_name =  self.comp_combobox.get()
        if self.controller.competition_name is not None:
            # self.comeptition_id = self.competition[self.competition['name']==self.competition_name].iloc[0]['id']
            self.controller.competition_id = utils.get_object_info(self.controller.session, Competition, name=self.controller.competition_name)[0].id
            self.report_frame = ttk.Frame(self)
            self.report_frame.grid(column=0, row=4, sticky='nsew')

            self.report_label = tk.Label(self.report_frame,text='select the path')
            self.report_label.grid(column=0, row=4, sticky='nsew')

            self.report_text = tk.Text(self.report_frame,state='disabled',height=1)
            self.report_text.grid(column=1, row=4, sticky='nsew')
            # self.schedule_text.pack(side='left')
            self.browse_button = ttk.Button(self.report_frame,text='browse', command=lambda: self.controller.select_folder(self.report_text))
            self.browse_button.grid(column=2, row=4, sticky='nsew')
        else:
            msg = 'please select the competition.'
            self.controller.insert_text(self.status_text, msg)
