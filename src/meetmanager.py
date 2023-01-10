import tkinter as tk

from sqlalchemy import create_engine
import toml
import pandas as pd

from gui.importschedulelayout import ImportScheduleLayout
from gui.importresultlayout import ImportResultLayout
from gui.processresult import ProcessResultLayout
from gui.eventheatresultlayout import GenerateEventHeatResultLayout
from gui.nextschedulelistlayout import GenerateNextScheduleListLayout
from gui.divisioneventresultlayout import GenerateDivisionEventResultLayout
from gui.meetdivisionresultlayout import GenerateMeetDivisionResultLayout


config_file = '/home/rhan/codes/dev/Skating/MeetOrganizer/config/config.toml'
with open(config_file, 'r') as conf:
    config = toml.load(conf)
engine = create_engine(f"{config['database']['protocol']}://{config['auth']['username']}:{config['auth']['password']}@{config['server']['host']}:{config['database']['port']}/{config['database']['db']}")

# engine = create_engine('sqlite:///skatemeet.db')

class App:
    def __init__(self, root, engine):
        self.root = root
        self.create_menu()
        self.create_main_frame()
        self.current_layout = None
        self.engine = engine
        self.meet = pd.read_sql_query('select "meet_ID", name from "Meet";', con=engine)
        # self.division = pd.read_sql_query('select "division_ID", name from "Division";', con=self.engine)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        action_menu = tk.Menu(menubar)
        menubar.add_cascade(label="Action", menu=action_menu)
        action_menu.add_command(label="Import Schedules", command=self.import_schedule_layout)
        action_menu.add_command(label="Import Results", command=self.import_result_layout)
        action_menu.add_command(label="Process Race Result", command=self.process_result)
        action_menu.add_command(label="Generate Event Heat Result", command=self.event_heat_result_layout)
        action_menu.add_command(label="Generate Next Schedule List", command=self.next_schedule_list_layout)
        action_menu.add_command(label="Generate Division Event Result", command=self.division_event_result_layout)
        action_menu.add_command(label="Generate Meet Result", command=self.meet_division_result_layout)

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid()

    # def show_layout(self, layout_class):
    #     if self.current_layout is not None:
    #         self.current_layout.clear()
    #     self.current_layout = layout_class(self.root, self.main_frame)
    
    def show_layout(self, layout_class):
        if self.current_layout is not None:
            self.current_layout.clear()
        self.current_layout = layout_class(self.root, self.main_frame, self.engine)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy

    def import_schedule_layout(self):
        self.show_layout(ImportScheduleLayout)

    def import_result_layout(self):
        self.show_layout(ImportResultLayout)

    def process_result(self):
        self.show_layout(ProcessResultLayout)

    def event_heat_result_layout(self):
        self.show_layout(GenerateEventHeatResultLayout)

    def next_schedule_list_layout(self):
        self.show_layout(GenerateNextScheduleListLayout)
    
    def division_event_result_layout(self):
        self.show_layout(GenerateDivisionEventResultLayout)

    def meet_division_result_layout(self):
        self.show_layout(GenerateMeetDivisionResultLayout)

root = tk.Tk()
root.title('Short Track Meet Organizer')
root.geometry('800x600')
app = App(root, engine)
root.mainloop()