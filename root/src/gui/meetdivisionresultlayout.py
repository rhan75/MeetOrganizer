import tkinter as tk
from tkinter import ttk

from .baselayer import BaseLayout
from skate import reports
from skate import utils

class GenerateMeetDivisionResultLayout(BaseLayout):
    def __init__(self, root, main_frame, engine):
        super().__init__(root, main_frame, engine)
        self.create_widgets()

    def create_widgets(self):

        self.clear_all()

        comp_text = tk.StringVar()

        self.title_label = tk.Label(self.main_frame, text='Generate Combined Result for the Competition', font=('helvetica', 24))
        self.title_label.grid(column=0, row=0)

        self.status_text = tk.Text(self.main_frame, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.insert_text('status_text', 'Ready to generate combined result for the competition')
        

        self.comp_frame = ttk.Frame(self.main_frame)
        self.comp_frame.grid(column=0, row=2, sticky='nsew')


        self.select_comp_label = tk.Label(self.comp_frame,text='select the competition')
        self.select_comp_label.grid(column=0, row=2, sticky='nsew')

        self.comp_combobox = ttk.Combobox(self.comp_frame, textvariable=comp_text)
        # self.comp_combobox['values'] = self.meet['name'].to_list()
        self.comp_combobox.grid(column=1, row=2, sticky='nsew')
        comp_text.set('select competition')
        self.comp_combobox['values'] = self.meet['name'].to_list()

        self.comp_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_competition)
        self.comp_combobox_button.grid(column=3, row=2, sticky='nsew')
        
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(column=0, row=5, sticky='nsew')

        #adding submit / export / clear / close buttons
        self.button_submit = ttk.Button(self.button_frame, text='submit', command=self.generate_report)
        self.button_submit.grid(column=0, row=5, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='clear', command=self.clear_selection('status_text'))
        self.button_clear.grid(column=2, row=5, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='close', command=self.root.destroy)
        self.button_close.grid(column=4, row=5, sticky='nsew')

    def generate_report(self):
        utils.create_meet_division_result(self.meet_ID, self.engine)
        utils.create_meet_division_result_detail(self.meet_ID, self.engine)
        utils.rank_meet_division_result(self.meet_ID, self.engine)

        reports.generate_meet_division_report(self.meet_ID, self.folder_name, self.engine)
        msg = f'The Combined Report for {self.meet_name} has been generated in {self.folder_name}'
        self.insert_text('status_text', msg)
    
    def select_competition(self):  
        self.meet_name =  self.comp_combobox.get()
        if self.meet_name is not None:
            self.meet_ID = self.meet[self.meet['name']==self.meet_name]['meet_ID'][0]

            self.report_frame = ttk.Frame(self.main_frame)
            self.report_frame.grid(column=0, row=4, sticky='nsew')

            self.report_label = tk.Label(self.report_frame,text='select the path')
            self.report_label.grid(column=0, row=4, sticky='nsew')

            self.report_text = tk.Text(self.report_frame,state='disabled',height=1)
            self.report_text.grid(column=1, row=4, sticky='nsew', pady=10)
            # self.schedule_text.pack(side='left')
            self.browse_button = ttk.Button(self.report_frame,text='browse', command=lambda: self.select_folder('report_text'))
            self.browse_button.grid(column=4, row=4, sticky='nsew')
        else:
            msg = 'please select the competition.'
            self.insert_text('status_text', msg)
