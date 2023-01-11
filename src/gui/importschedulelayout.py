import tkinter as tk
from tkinter import ttk

from .baselayer import BaseLayout
from skate import utils
# from connection import create_connection

class ImportScheduleLayout(BaseLayout):
    def __init__(self, root, main_frame, engine):
        super().__init__(root, main_frame, engine)
        self.create_widgets()

    def create_widgets(self):
        # create the widgets for the import schedule layout

        self.clear_all()
        self.clear()
        
        self.import_schedule_label = tk.Label(self.main_frame, text='Import Schedule', font=('Helvetica', 24))
        self.import_schedule_label.grid(column=0, row=0)
        # self.import_schedule_label.pack(side='top')
 
        # self.schedule_label.pack(side='left')
        self.schedule_text = tk.Text(self.main_frame,state='disabled',height=1)
        self.schedule_text.grid(column=0, row=1, sticky='nsew')
        # self.schedule_text.pack(side='left')
        self.browse_button = ttk.Button(self.main_frame,text='Browse', command=lambda: self.select_file('schedule_text'))
        self.browse_button.grid(column=1, row=1, sticky='nsew')
        # self.browse_button.pack(side='right')

        #Adding Submit / Export / Clear / Close buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(column=0, row=2, sticky='nsew')

        #Adding Submit / Export / Clear / Close buttons
        self.button_submit = ttk.Button(self.button_frame, text='Submit', command=lambda: self.process_schedule('schedule_text'))
        self.button_submit.grid(column=0, row=2, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='Clear', command=lambda: self.clear_selection('schedule_text'))
        self.button_clear.grid(column=1, row=2, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='Close', command=self.root.destroy)
        self.button_close.grid(column=2, row=2, sticky='nsew')

    def process_schedule(self, textbox:str):
        if self.filename:
            # process_schedule(self.filename)
            schedule = utils.import_schedule(self.filename)
            utils.create_race_heat_schedule_and_detail(schedule, self.engine)
            result = 'Processed'
        else:
            result = 'Aborted: No file selected'
        self.insert_text(textbox, result)
