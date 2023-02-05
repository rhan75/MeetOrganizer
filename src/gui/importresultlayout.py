import tkinter as tk
from tkinter import ttk
import os

from skate import utils

class ImportResultLayout(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # self.controller.clear_all()
        # self.controller.clear()
        # create the widgets for the import schedule layout
        if hasattr(self, 'result_text'):
            self.clear_all()
       
        
        self.result_label = tk.Label(self, text='Import Results', font=('Helvetica', 24))
        self.result_label.grid(column=0, row=0)
        self.result_text = tk.Text(self, state='disabled', height=1)
        self.result_text.grid(column=0, row=1, sticky='nsew')
        self.controller.insert_text(self.result_text, 'Select the result folder that contains result files.')
        self.result_button = ttk.Button(self, text='Browse', command=lambda: self.controller.select_folder(self.result_text))
        self.result_button.grid(column=1, row=1, sticky='nsew')
        
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(column=0, row=2, sticky='nsew')

        #Adding Submit / Export / Clear / Close buttons
        self.button_submit = ttk.Button(self.button_frame, text='Submit', command=lambda: self.process_result(self.result_text))
        self.button_submit.grid(column=0, row=2, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='Clear', command=self.clear_all)
        self.button_clear.grid(column=1, row=2, sticky='nsew')
    
        self.button_main = ttk.Button(self.button_frame, text='Main', command=lambda: self.controller.show_frame("MainScreenLayout"))
        self.button_main.grid(column=2, row=2, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='Close', command=self.controller.destroy)
        self.button_close.grid(column=3, row=2, sticky='nsew')

    def clear_all(self):
        self.controller.clear_all()
        self.controller.insert_text(self.result_text, 'Select the result folder that contains result files.')

    def process_result(self, textbox:str):
        if self.controller.directory:
            os.chdir(self.controller.directory)
            for file in os.listdir(self.controller.directory):
                result_file = os.path.join(self.controller.directory,file)
                #print(result_file)
                update_result = utils.create_race_heat_result(result_file, self.controller.engine)
                #print(rhs_rhr)
                if update_result['status'] == 'success':
                    utils.create_race_heat_result_detail(result_file, update_result, self.controller.engine)
                    result = 'Processed'
                else:
                    result = f'Error: {result_file}'
        else:
            result = 'Aborted: No folder selected'
        self.controller.insert_text(textbox, result)