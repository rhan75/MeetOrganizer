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

        text_font = ('Time New Roman', 12, 'bold')
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, columnspan=3, sticky='nsew')

        self.main_label = tk.Label(self.main_frame, text='Skate Competition Manager', font=('Arial', 36))
        self.main_label.grid(row=0, sticky='nsew')
        self.main_label2 = tk.Label(self.main_frame)
        self.main_label2.grid(row=1, sticky='nsew')
                
        self.import_frame = tk.Frame(self, height=400)
        self.import_frame.grid(row=2, column=0, sticky='n')
        self.import_label = tk.Label(self.import_frame, text='Import Section', font=text_font)
        self.import_label.grid(row=2, column=0, sticky='n')

        self.process_frame = tk.Frame(self, height=400)
        self.process_frame.grid(row=2, column=1, sticky='n')
        self.process_label = tk.Label(self.process_frame, text='Process Section', font=text_font)
        self.process_label.grid(row=2, column=1, sticky='n')

        self.report_frame = tk.Frame(self, height=400)
        self.report_frame.grid(row=2, column=2, sticky='n')
        self.report_label = tk.Label(self.report_frame, text='Import Section', font=text_font)
        self.report_label.grid(row=2, column=2, sticky='n')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.schedule_button = ttk.Button(self.import_frame, text='Import Schedules', command=lambda: self.controller.show_frame('ImportScheduleLayout'))
        self.schedule_button.grid(column=0, row=3, sticky='nsew')

        self.result_button = ttk.Button(self.import_frame, text='Import Results', command=self.controller.import_result_layout)
        self.result_button.grid(column=0, row=4, sticky='nsew')

        self.event_result_button = ttk.Button(self.process_frame, text="Process Event Results", command=self.controller.process_event_result)
        self.event_result_button.grid(column=1, row=3, sticky='nsew')

        self.process_final_comp_button = ttk.Button(self.process_frame, text="Process Final Competition Results", command=self.controller.process_competition_result)
        self.process_final_comp_button.grid(column=1, row=4, sticky='nsew')

        self.event_heat_result_button = ttk.Button(self.report_frame, text="Generate Event Heat Result", command=self.controller.event_heat_result_layout)
        self.event_heat_result_button.grid(column=2, row=3, sticky='nsew')

        self.next_schedule_button = ttk.Button(self.report_frame, text="Generate Next Schedule List", command=self.controller.next_schedule_list_layout)
        self.next_schedule_button.grid(column=2, row=4, sticky='nsew')

        self.ag_event_result_button = ttk.Button(self.report_frame, text="Generate Age Group Event Result", command=self.controller.age_group_event_result_layout)
        self.ag_event_result_button.grid(column=2, row=5, sticky='nsew')

        self.comp_ag_result_button = ttk.Button(self.report_frame, text="Generate Competition Result", command=self.controller.competition_age_group_result_layout)
        self.comp_ag_result_button.grid(column=2, row=6, sticky='nsew')

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=7, sticky='nsew')


        self.button_close = ttk.Button(self.button_frame, text='Exit', command=self.controller.destroy)
        self.button_close.grid(column=0, row=6, sticky='nsew')
    
    def clear_all(self):
        self.controller.clear_all()
