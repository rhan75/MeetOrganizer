import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askdirectory

from sqlalchemy.orm import aliased
from sqlalchemy.engine.base import Engine


from gui.mainscreenlayout import MainScreenLayout
from gui.importschedulelayout import ImportScheduleLayout
from gui.importresultlayout import ImportResultLayout
from gui.processagegroupresult import ProcessAgeGroupResultLayout
from gui.processcompetitionresult import ProcessCompetitionResultLayout 
from gui.eventheatresultlayout import GenerateEventHeatResultLayout
from gui.nextschedulelistlayout import GenerateNextScheduleListLayout
from gui.agegroupeventresultlayout import GenerateAgeGroupEventResultLayout
from gui.competitionagegroupresultlayout import GenerateCompetitionAgeGroupResultLayout

from models.model import *
from models.aliases import *
from skate import utils


# engine = create_engine('sqlite:///skatecompetition.db')


class App(tk.Tk):
    def __init__(self, engine, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.AG = aliased(Age_Group)
        self.AGC = aliased(Age_Group_Class)

        self.CS = aliased(Competition_Skater)
        self.CAGR = aliased(Competition_Age_Group_Result)
        self.CAGRD = aliased(Competition_Age_Group_Result_Detail)

        self.RHS = aliased(Race_Heat_Schedule)
        self.RHR = aliased(Race_Heat_Result)
        self.RHRD = aliased(Race_Heat_Result_Detail)
        self.RAGR = aliased(Race_Age_Group_Result)
        self.RHSD = aliased(Race_Heat_Schedule_Detail)
        self.RAGRD = aliased(Race_Age_Group_Result_Detail)
        self.RS = aliased(Race_Style)
        self.Skater = Skater
        self.Competition = Competition
        self.Race = Race
        self.Heat = Heat
        self.Lane = Lane
        self.Gender = Gender
        self.engine = engine
        self.filename = None
        self.result = None
        self.directory = None
        self.competition_id = None
        self.competition_name = None
        self.event = None
        self.gender = None
        self.competitions = None
        self.session = None
        
        self.create_const()
        self.create_menu()
        
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainScreenLayout, ImportScheduleLayout, ImportResultLayout, ProcessAgeGroupResultLayout, \
            ProcessCompetitionResultLayout, GenerateEventHeatResultLayout, GenerateNextScheduleListLayout, \
            GenerateAgeGroupEventResultLayout, GenerateCompetitionAgeGroupResultLayout):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nswe")
        self.show_frame("MainScreenLayout")

    def create_const(self):
        self.session = utils.prep_session(self.engine)
        self.competitions = utils.get_object_info(self.session, self.Competition)
        
    def show_frame(self, name):
        frame = self.frames[name]
        frame.clear_all()
        # print('Changing')
        # print(name)
        # print(self.frames[name])
        frame.tkraise()

        # create the widgets for the import schedule layout

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        action_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Action", menu=action_menu)
        action_menu.add_command(label="Main", command=self.main_screen_layout)
        action_menu.add_command(label="Import Schedules", command=self.import_schedule_layout)
        action_menu.add_command(label="Import Results", command=self.import_result_layout)
        action_menu.add_command(label="Process Event Results", command=self.process_event_result)
        action_menu.add_command(label="Process Final Competition Results", command=self.process_competition_result)
        action_menu.add_command(label="Generate Event Heat Result", command=self.event_heat_result_layout)
        action_menu.add_command(label="Generate Next Schedule List", command=self.next_schedule_list_layout)
        action_menu.add_command(label="Generate Age Group Event Result", command=self.age_group_event_result_layout)
        action_menu.add_command(label="Generate Competition Result", command=self.competition_age_group_result_layout)
    
    def main_screen_layout(self):
        self.show_frame("MainScreenLayout")

    def import_schedule_layout(self):
        self.show_frame("ImportScheduleLayout")

    def import_result_layout(self):
        self.show_frame("ImportResultLayout")

    def process_event_result(self):
        self.show_frame("ProcessAgeGroupResultLayout")

    def process_competition_result(self):
        self.show_frame("ProcessCompetitionResultLayout")

    def event_heat_result_layout(self):
        self.show_frame("GenerateEventHeatResultLayout")

    def next_schedule_list_layout(self):
        self.show_frame("GenerateNextScheduleListLayout")
    
    def age_group_event_result_layout(self):
        self.show_frame("GenerateAgeGroupEventResultLayout")

    def competition_age_group_result_layout(self):
        self.show_frame("GenerateCompetitionAgeGroupResultLayout")

    def select_competition(self, comp_combobox, text_box, next_function):  
        self.competition_name = comp_combobox.get()
        #print(self.competition_name)
        if self.competition_name is not None:
            self.competition_id = utils.get_object_info(self.session, Competition, name=self.competition_name)[0].id
            next_function()
            
        else:
            msg = 'please select the competition.'
            self.insert_text(text_box, msg)

    def select_event(self, event_combobox, text_box, next_function):
        self.event = event_combobox.get()

        if self.event is not None:
            next_function()
        else:
            msg = 'please select the event.'
            self.insert_text(text_box, msg)

    # def show_event_selector(self, event_label, event_combobox, combobox_button):
    #     evtrace = utils.get_object_info(self.controller.session, Race_Heat_Schedule, competition_id=self.controller.competition_id)
    #     event_race = set(row.event for row in evtrace)
    #     values = [row for row in event_race]
    #     values.sort()
    #     # event_text = tk.StringVar()

    #     event_label.config(text='Select the event')
    #     event_combobox['values'] = values

    #     # values = None

    #     combobox_button.config(text='Select', command=self.select_event)

    def insert_text(self, widget, text):
        # widget = getattr(self, textbox)
        widget.configure(state='normal')
        widget.delete('1.0', tk.END)
        widget.insert(tk.END, text)
        widget.configure(state='disabled')
    
    def select_file(self, textbox):
        self.filename = askopenfilename()
        self.insert_text(textbox, self.filename)
    
    def clear_all(self):
        self.filename = None
        self.result = None
        self.directory = None
        self.competition_id = None
        self.competition_name = None
        self.event = None
        self.gender = None
        self.competitions = None
        self.create_const()

        # self.competition = None
        # self.engine = None
    
    def clear_selection(self, textbox):
        self.clear_all()
        self.insert_text(textbox, '')

    def select_folder(self, textbox):
        self.directory = askdirectory()
        self.insert_text(textbox, self.directory)

    # def show_report_folder_selector(self):
    #     self.low_age_group = utils.get_object_info(self.controller.session, Age_Group, name=self.age_group_low_name)[0].id
    #     self.high_age_group = utils.get_object_info(self.controller.session, Age_Group, name=self.age_group_high_name)[0].id

    #     self.age_group_range = {'low_age_group': {'name':self.age_group_low_combobox.get(), 'ag_id':self.low_age_group}, 'high_age_group': {'name':self.age_group_high_combobox.get(), 'ag_id':self.high_age_group}}
        
    #     self.report_frame = ttk.Frame(self)
    #     self.report_frame.grid(column=0, row=5, sticky='nsew')


    #     self.report_label = tk.Label(self.report_frame,text='select the path')
    #     self.report_label.grid(column=0, row=5, sticky='nsew')

    #     self.report_text = tk.Text(self.report_frame,state='disabled',height=1)
    #     self.report_text.grid(column=1, row=5, sticky='nsew')
    #     # self.schedule_text.pack(side='left')
    #     self.browse_button = ttk.Button(self.report_frame,text='browse', command=lambda: self.controller.select_folder(self.report_text))
    #     self.browse_button.grid(column=2, row=5, sticky='nsew')
