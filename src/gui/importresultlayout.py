import tkinter as tk
from tkinter import ttk
import os

from .baselayer import BaseLayout
from skate import utils

class ImportResultLayout(BaseLayout):
    def __init__(self, root, main_frame, engine):
        super().__init__(root, main_frame, engine)
        self.create_widgets()

    def create_widgets(self):
        self.clear_all()
        # create the widgets for the import schedule layout
       
        self.result_label = tk.Label(self.main_frame, text='Import Results', font=('Helvetica', 24))
        self.result_label.grid(column=0, row=0)
        self.result_text = tk.Text(self.main_frame, state='disabled', height=1)
        self.result_text.grid(column=0, row=1, columnspan=3, sticky='W', pady=10)
        self.result_button = ttk.Button(self.main_frame, text='Browse', command=lambda: self.select_folder('result_text'))
        self.result_button.grid(column=4, row=1, sticky='W')
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(column=0, row=2, sticky='W')

        #Adding Submit / Export / Clear / Close buttons
        self.button_submit = ttk.Button(self.button_frame, text='Submit', command=lambda: self.process_result('result_text'))
        self.button_submit.grid(column=0, row=2, sticky='W')

        self.button_clear = ttk.Button(self.button_frame, text='Clear', command=lambda: self.clear_selection('result_text'))
        self.button_clear.grid(column=2, row=2, sticky='W')

        self.button_close = ttk.Button(self.main_frame, text='Close', command=self.root.destroy)
        self.button_close.grid(column=4, row=2, sticky='E')

    def process_result(self, textbox:str):
        if self.folder_name:
            os.chdir(self.folder_name)
            for file in os.listdir(self.folder_name):
                result_file = os.path.join(self.folder_name,file)
                #print(result_file)
                rhs_rhr = utils.create_race_heat_result(result_file, self.engine)
                #print(rhs_rhr)
                utils.create_race_heat_result_detail(result_file, rhs_rhr, self.engine)
            result = 'Processed'
        else:
            result = 'Aborted: No folder selected'
        self.insert_text(textbox, result)