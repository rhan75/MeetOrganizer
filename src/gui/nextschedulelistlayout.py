import tkinter as tk
from tkinter import ttk

from .baselayer import BaseLayout
from skate import reports

class GenerateNextScheduleListLayout(BaseLayout):
    def __init__(self, root, main_frame, engine):
        super().__init__(root, main_frame, engine)
        self.create_widgets()
        self.low_age_group = None
        self.high_age_group = None
        self.age_group_range = None

    def create_widgets(self):

        self.clear_all()
        self.clear()

        comp_text = tk.StringVar()

        self.title_label = tk.Label(self.main_frame, text='Generate Next Schedule List', font=('helvetica', 24))
        self.title_label.grid(column=0, row=0, sticky='nsew')

        self.status_text = tk.Text(self.main_frame, height=1)
        self.status_text.grid(column=0, row=1, sticky='nsew')
        self.insert_text('status_text', 'Ready to generate event results for age_groups')
        

        self.comp_frame = ttk.Frame(self.main_frame)
        self.comp_frame.grid(column=0, row=2, sticky='nsew')


        self.select_comp_label = tk.Label(self.comp_frame,text='select the competition')
        self.select_comp_label.grid(column=0, row=2, sticky='nsew')

        self.comp_combobox = ttk.Combobox(self.comp_frame, textvariable=comp_text)
        
        self.comp_combobox.grid(column=1, row=2, sticky='nsew')
        comp_text.set('select competition')
        self.comp_combobox['values'] = [row.name for row in self.competition]
        # self.comp_combobox['values'] = self.competition['name'].to_list()

        self.comp_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_competition)
        self.comp_combobox_button.grid(column=2, row=2, sticky='nsew')
        
        
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(column=0, row=6, sticky='nsew')

        #adding submit / export / clear / close buttons
        self.button_submit = ttk.Button(self.button_frame, text='submit', command=self.generate_report)
        self.button_submit.grid(column=0, row=6, sticky='nsew')

        self.button_clear = ttk.Button(self.button_frame, text='clear', command=self.reload_frame)
        self.button_clear.grid(column=1, row=6, sticky='nsew')

        self.button_close = ttk.Button(self.button_frame, text='close', command=self.root.destroy)
        self.button_close.grid(column=2, row=6, sticky='nsew')

    def reload_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy
        self.create_widgets()

    def generate_report(self):
        reports.generate_event_schedule_list_report(self.competition_id, self.event, self.folder_name, self.age_group_range, self.engine)
        # self.competition_name = self.competition[self.competition['id']==self.competition_id]['name'][0]
        msg = f'Result for event {self.event} from {self.competition_name} has been generated in {self.folder_name}'
        self.insert_text('status_text', msg)
    
    def select_competition(self):  
        self.competition_name =  self.comp_combobox.get()
        #print(self.competition_name)
        if self.competition_name is not None:
            # self.competition_id = self.competition[self.competition['name']==self.competition_name].iloc[0]['id']
            self.competition_id = self.session.query(self.Competition).where(self.Competition.name==self.competition_name).first().id
        
            event_race = self.session.query(self.RHS.event).where(self.RHS.competition_id==self.competition_id).distinct().all()
            # event_race = pd.read_sql_query(f'select distinct event from race_heat_schedule where competition_id = {self.competition_id};', self.engine)
            event_text = tk.StringVar()


            self.event_frame = ttk.Frame(self.main_frame)
            self.event_frame.grid(column=0, row=3, sticky='nsew')


            self.select_event_label = tk.Label(self.comp_frame,text='select the event')
            self.select_event_label.grid(column=0, row=3, sticky='nsew')

            self.event_combobox = ttk.Combobox(self.comp_frame, textvariable=event_text)
            # values = event_race['event'].to_list() #event value
            values = [row.event for row in event_race]
            values.sort()
            self.event_combobox['values'] = values
            values = None
            self.event_combobox.grid(column=1, row=3, sticky='nswe')
            event_text.set('select competition')

            self.event_combobox_button = ttk.Button(self.comp_frame, text='select', command=self.select_event)
            self.event_combobox_button.grid(column=2, row=3, sticky='w')
        else:
            msg = 'please select the competition.'
            self.insert_text('status_text', msg)

    def select_event(self):
        self.event = self.event_combobox.get()
        age_group = self.session.query(self.AG.id, self.AG.name).all()

        # age_group = pd.read_sql_query('select id, name from age_group;', con=self.engine)
        
        self.age_group_frame = ttk.Frame(self.main_frame)
        self.age_group_frame.grid(column=0, row=4, sticky='nsew')


        self.age_group_label = tk.Label(self.age_group_frame,text='select the range of age groups')
        self.age_group_label.grid(column=0, row=4, sticky='nsew')

        age_group_low_text = tk.StringVar()
        age_group_high_text = tk.StringVar()
        
        age_group_names = [row.name for row in age_group]
        self.age_group_low_combobox = ttk.Combobox(self.age_group_frame, textvariable=age_group_low_text )
        self.age_group_low_combobox.grid(column=1, row=4, sticky='nsew')
        self.age_group_low_combobox['values'] = age_group_names
        # age_group['name'].to_list()
        age_group_low_text.set('Select the lower age_group')

        self.age_group_high_combobox = ttk.Combobox(self.age_group_frame, textvariable=age_group_high_text )
        self.age_group_high_combobox.grid(column=2, row=4, sticky='nsew')
        self.age_group_high_combobox['values'] = age_group_names
        age_group_high_text.set('Select the higher age_group')
                
        self.age_group_combobox_button = ttk.Button(self.age_group_frame,text='select', command=self.select_age_group)
        self.age_group_combobox_button.grid(column=3, row=4, sticky='nsew')

    def select_age_group(self):
        # age_group = pd.read_sql_query('select id, name from age_group;', con=self.engine)
        # age_group = self.session.query(self.AG.id, self.AG.name).all()
        # low = age_group[age_group['name']== self.age_group_low_combobox.get()].head(1)
        self.low_age_group = self.session.query(self.AG.id).where(self.AG.name == self.age_group_low_combobox.get()).first().id
        # high = age_group[age_group['name']== self.age_group_high_combobox.get()].head(1)
        self.high_age_group = self.session.query(self.AG.id).where(self.AG.name == self.age_group_high_combobox.get()).first().id
        # self.low_age_group = low['id'].iloc[0]
        # self.high_age_group = high['id'].iloc[0]
        self.age_group_range = {'low_age_group': {'name':self.age_group_low_combobox.get(), 'ag_id':self.low_age_group}, 'high_age_group': {'name':self.age_group_high_combobox.get(), 'ag_id':self.high_age_group}}
        
        self.report_frame = ttk.Frame(self.main_frame)
        self.report_frame.grid(column=0, row=5, sticky='nsew')


        self.report_label = tk.Label(self.report_frame,text='select the path')
        self.report_label.grid(column=0, row=5, sticky='nsew')

        self.report_text = tk.Text(self.report_frame,state='disabled',height=1)
        self.report_text.grid(column=1, row=5, sticky='nsew')
        # self.schedule_text.pack(side='left')
        self.browse_button = ttk.Button(self.report_frame,text='browse', command=lambda: self.select_folder('report_text'))
        self.browse_button.grid(column=2, row=5, sticky='nsew')