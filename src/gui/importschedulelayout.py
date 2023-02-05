import tkinter as tk
from tkinter import ttk

from skate import utils
# from connection import create_connection

class ImportScheduleLayout(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):

        if hasattr(self, 'schedule_text'):
            self.clear_all()
        # create the widgets for the import schedule layout
        
        self.import_schedule_label = tk.Label(self, text='Import Schedule', font=('Arial', 24))
        self.import_schedule_label.grid(column=0, row=0)

        # self.import_schedule_label.pack(side='top')
 
        # self.schedule_label.pack(side='left')
        self.schedule_text = tk.Text(self,state='disabled',height=1)
        self.schedule_text.grid(column=0, row=1, sticky='nsew')
        self.controller.insert_text(self.schedule_text, 'Select the schedule file.')
        # self.schedule_text.pack(side='left')
        self.browse_button = ttk.Button(self,text='Browse', command=lambda: self.controller.select_file(self.schedule_text))
        self.browse_button.grid(column=1, row=1, sticky='nsew')
        # self.browse_button.pack(side='right')

        #Adding Submit / Export / Clear / Close buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=2, sticky='nsew')

        #Adding Submit / Export / Clear / Close buttons
        self.button_submit = ttk.Button(self.button_frame, text='Submit', command=lambda: self.process_schedule(self.schedule_text))
        self.button_submit.grid(column=0, row=2, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='Clear', command=self.clear_all)
        self.button_clear.grid(column=1, row=2, sticky='nsew')

        self.button_main = ttk.Button(self.button_frame, text='Main', command=lambda: self.controller.show_frame("MainScreenLayout"))
        self.button_main.grid(column=2, row=2, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='Close', command=self.controller.destroy)
        self.button_close.grid(column=3, row=2, sticky='nsew')

    def clear_all(self):
        self.controller.clear_all()
        self.controller.insert_text(self.schedule_text, 'Select the schedule file.')

    def process_schedule(self, textbox):
        if self.controller.filename:
            # process_schedule(self.filename)
            utils.import_schedule(self.controller.filename, self.controller.engine)
            # utils.create_race_heat_schedule_and_detail(schedule, self.engine)
            result = 'Processed'
        else:
            result = 'Aborted: No file selected'
        self.controller.insert_text(textbox, result)
