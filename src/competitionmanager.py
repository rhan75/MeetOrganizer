from sqlalchemy import create_engine
import toml
from gui.controller import App

def main(engine):
    app = App(engine=engine)
    app.title('Short Track Competition Organizer')
    app.geometry('800x600')
    app.mainloop()


if __name__=="__main__":
    config_file = '/home/rhan/codes/dev/Skating/MeetOrganizer/config/config.toml'
    with open(config_file, 'r') as conf:
        config = toml.load(conf)
    engine = create_engine(f"{config['database']['protocol']}://{config['auth']['username']}:{config['auth']['password']}@{config['server']['host']}:{config['database']['port']}/{config['database']['db']}")

    main(engine)