import tkinter as tk
from tkinter import ttk

from skate.model import *
from skate.utils import *

class MainScreenLayout(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.main_label = tk.Label(self, text='Skate Competition Manager', font=('Helvetica', 36))
        self.main_label.grid(column=0, row=0, sticky='nsew')
        
        self.action_frame = tk.Frame(self)
        self.action_frame.grid(column=0, row=1, sticky='nsew')

        self.schedule_button = ttk.Button(self.action_frame, text='Import Schedules', command=lambda: self.controller.show_frame('ImportScheduleLayout'))
        self.schedule_button.grid(column=0, row=1, sticky='nsew')

        self.result_button = ttk.Button(self.action_frame, text='Import Results', command=self.controller.import_result_layout)
        self.result_button.grid(column=1, row=1, sticky='nsew')

        self.event_result_button = ttk.Button(self.action_frame, text="Process Event Results", command=self.controller.process_event_result)
        self.event_result_button.grid(column=2, row=1, sticky='nsew')

        self.process_final_comp_button = ttk.Button(self.action_frame, text="Process Final Competition Results", command=self.controller.process_competition_result)
        self.process_final_comp_button.grid(column=3, row=1, sticky='nsew')

        self.event_heat_result_button = ttk.Button(self.action_frame, text="Generate Event Heat Result", command=self.controller.event_heat_result_layout)
        self.event_heat_result_button.grid(column=0, row=2, sticky='nsew')

        self.next_schedule_button = ttk.Button(self.action_frame, text="Generate Next Schedule List", command=self.controller.next_schedule_list_layout)
        self.next_schedule_button.grid(column=1, row=2, sticky='nsew')

        self.ag_event_result_button = ttk.Button(self.action_frame, text="Generate Age Group Event Result", command=self.controller.age_group_event_result_layout)
        self.ag_event_result_button.grid(column=2, row=2, sticky='nsew')

        self.comp_ag_result_button = ttk.Button(self.action_frame, text="Generate Competition Result", command=self.controller.competition_age_group_result_layout)
        self.comp_ag_result_button.grid(column=3, row=2, sticky='nsew')

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=3, sticky='nsew')

        self.button_submit = ttk.Button(self.button_frame, text='Submit', command=lambda: self.process_result(self.result_text))
        self.button_submit.grid(column=0, row=2, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='Clear', command=lambda: self.controller.clear_selection(self.result_text))
        self.button_clear.grid(column=1, row=2, sticky='nsew')
    
        self.button_main = ttk.Button(self.button_frame, text='Main', command=lambda: self.controller.show_frame("MainScreen"))
        self.button_main.grid(column=2, row=2, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='Close', command=self.controller.destroy)
        self.button_close.grid(column=3, row=2, sticky='nsew')