import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
import pandas as pd
#from connection import create_connection

class BaseLayout:
    def __init__(self, root, main_frame, engine):
        self.root = root
        self.main_frame = main_frame
        self.filename = None
        self.result = None
        self.directory = None
        self.competition_ID = None
        self.event = None
        self.gender = None
        self.competition_name = None
        self.meet = pd.read_sql_query('select "competition_ID", name from competition;', con=engine)
        self.engine = engine


    def clear(self):
        # destroy all of the widgets in the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def insert_text(self, textbox, text):
        widget = getattr(self, textbox)
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
        self.competition_ID = None
        self.event = None
        self.gender = None
        self.competition_name = None
        # self.meet = None
        # self.engine = None
    
    def clear_selection(self, textbox: str):
        self.clear_all()
        self.insert_text(textbox, '')

    def select_folder(self, textbox):
        self.folder_name = askdirectory()
        self.insert_text(textbox, self.folder_name)