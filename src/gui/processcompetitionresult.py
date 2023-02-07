import tkinter as tk
from tkinter import ttk
from skate import utils

from models.model import *
from skate.utils import * 

class ProcessCompetitionResultLayout(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):

        comp_text = tk.StringVar()

        self.title_label = tk.Label(self, text='Process Final Competition Result', font=('Arial', 24))
        self.title_label.grid(column=0, row=0)

        self.status_text = tk.Text(self, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.controller.insert_text(self.status_text, 'Ready to process imported results for event')
        

        self.comp_frame = ttk.Frame(self)
        self.comp_frame.grid(column=0, row=2, sticky='nsew')


        self.select_comp_label = tk.Label(self.comp_frame,text='select the competition')
        self.select_comp_label.grid(column=0, row=2, sticky='nsew')

        self.comp_combobox = ttk.Combobox(self.comp_frame, textvariable=comp_text)

        self.comp_combobox.grid(column=1, row=2, sticky='nsew')
        comp_text.set('select competition')
        self.comp_combobox['values'] = [row.name for row in self.controller.competitions]

        self.comp_combobox_button = ttk.Button(self.comp_frame, text='select', command=lambda: self.select_competition(self.status_text))
        self.comp_combobox_button.grid(column=2, row=2, sticky='nsew')
        
        
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=5, sticky='nsew')

        #adding submit / export / clear / close buttons
        self.button_submit = ttk.Button(self.button_frame, text='submit', command=lambda: self.process_results(self.status_text))
        self.button_submit.grid(column=0, row=5, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='clear', command=self.clear_all())
        self.button_clear.grid(column=1, row=5, sticky='nsew')
    
        self.button_main = ttk.Button(self.button_frame, text='Main', command=lambda: self.controller.show_frame("MainScreenLayout"))
        self.button_main.grid(column=2, row=5, sticky='nsew')   

        self.button_close = ttk.Button(self.button_frame, text='close', command=self.controller.destroy)
        self.button_close.grid(column=3, row=5, sticky='nsew')

    def clear_all(self):
        self.controller.clear_all()
        self.controller.insert_text(self.status_text, 'Ready to process imported results for event')

    def process_results(self, textbox):
        utils.create_competition_age_group_result(self.controller.competition_id, self.controller.engine)
        utils.create_competition_age_group_result_detail(self.controller.competition_id, self.controller.engine)
        utils.rank_competition_age_group_result(self.controller.competition_id, self.controller.engine)
        msg = f'{self.controller.competition_name}\'s final results have been processed'
        self.controller.insert_text(textbox, msg)
    
    def select_competition(self, textbox):  
        self.controller.competition_name =  self.comp_combobox.get()
        if self.controller.competition_name is not None:
            self.controller.competition_id = get_object_info(self.controller.session, Competition, name=self.controller.competition_name)[0].id 
            self.controller.insert_text(textbox, f'{self.controller.competition_name} selected.')
        else:
            msg = 'please select the competition.'
            self.controller.insert_text(textbox, msg)


