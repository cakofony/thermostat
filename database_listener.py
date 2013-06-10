import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.dialects.mysql import FLOAT, INTEGER, DATETIME, BOOLEAN
import datetime
import ConfigParser
import sys


TEMP_TABLE = 'temperature'
SETTINGS_TABLE = 'settings'
CLIMATE_CONTROL_TABLE = 'climatecontrol'
class DatabaseListener:

    def __init__(self):
        cfgparser = ConfigParser.ConfigParser()
        cfgparser.readfp(open('database.cfg'))
        self.DB_NAME = cfgparser.get('database', 'address')
        self.DB_USER = cfgparser.get('database', 'username')
        self.DB_PASS = cfgparser.get('database', 'password')
        try:
            self.setup_db()
            self.build_tables()
        except:
            print 'failed to set up database'

    def setup_db(self):
        try:
            self.engine = create_engine('mysql://%s:%s@%s?charset=utf8&use_unicode=1' % (self.DB_USER, self.DB_PASS, self.DB_NAME))
            self.connection = self.engine.connect()
            self.meta = MetaData()
            self.meta.bind = self.connection
        except Exception as ex:
            print ex
            sys.exit(1)

    def teardown_db(self):
        self.connection.close()

    def build_tables(self):
        self.temperature = Table(TEMP_TABLE, self.meta,
                Column('temperature', FLOAT(6,3)),
                Column('timestamp', DATETIME, default=datetime.datetime.now()))
        
        self.settings = Table(SETTINGS_TABLE, self.meta,
                Column('min_temp', FLOAT(6,3)),
                Column('max_temp', FLOAT(6,3)),
                Column('system', BOOLEAN),
                Column('fan', BOOLEAN),
                Column('timestamp', DATETIME, default=datetime.datetime.now())
                )

        self.climate = Table(CLIMATE_CONTROL_TABLE, self.meta,
                Column('fan', BOOLEAN),
                Column('ac', BOOLEAN),
                Column('heat', BOOLEAN),
                Column('timestamp', DATETIME, default=datetime.datetime.now()))

        self.meta.create_all(self.engine)

    def get_table(self, table_name):
        return Table(table_name, self.meta, autoload=True)

    def update_temperature(self, temp):
        try:
            self.engine.execute(self.temperature.insert(), temperature=temp)
        except:
            print 'failed to write temp'

    def settings_changed(self, conf):
        try:
            self.engine.execute(self.settings.insert(), min_temp=conf.mint, max_temp=conf.maxt, system=conf.system, fan=conf.fan)
        except:
            print 'failed to write settings'

    def update_active(self, result, heat, cool, fan):
        try:
            self.engine.execute(self.climate.insert(), fan=fan, heat=heat, ac=cool)
        except:
            print 'failed to write climate controller status'

db = DatabaseListener()
db.update_temperature(50.123)
from settings import Settings
s = Settings()
s.register_observer(db)
s.set_all(60, 70, False, True)
db.update_active('meh', True, False, True)
db.teardown_db()
