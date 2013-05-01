import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.dialects.mysql import FLOAT, INTEGER, DATETIME, BOOLEAN
import datetime

DB_NAME = '127.0.0.1/localdb'
DB_USER = 'root'
DB_PASS = 'c4kofony'

TEMP_TABLE = 'temperature'
SETTINGS_TABLE = 'settings'
CLIMATE_CONTROL_TABLE = 'climatecontrol'

class DatabaseListener:

    def __init__(self):
        self.setup_db()
        self.build_tables()

    def setup_db(self):
        try:
            self.engine = create_engine('mysql://%s:%s@%s?charset=utf8&use_unicode=0' % (DB_USER, DB_PASS, DB_NAME))
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

    
db = DatabaseLogger()
db.teardown_db()
