import psycopg2

class Postgresql:
    def __init__(self, DB_NAME, DB_USER, PASSWORD):
        self.db = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                                   password=PASSWORD, host='localhost')
        self.db.autocommit = True

        self.cursor = self.db.cursor()
        cursor = self.cursor

        cursor.execute('Create table if not exists CLIENT ( \
                        LOGIN varchar(100) primary key, \
                        PASSWORD varchar(64) not null, \
                        IS_TIME_PASSWORD boolean not null, \
                        GMT integer check (GMT >= -12 and GMT <= 14), \
                        CHAT_ID varchar(15) not null \
                        );')

        cursor.execute('Create table if not exists ALARMCLOCK ( \
                        ID serial primary key, \
                        LOGIN varchar(100) references CLIENT (LOGIN), \
                        TIME timestamp not null, \
                        TEXT varchar(1000) \
                        );')
        
        cursor.execute('Create table if not exists LOGIN_SESSION ( \
                        LOGIN varchar(100) references CLIENT (LOGIN), \
                        SESSION varchar(50) primary key, \
                        IS_FOR_CHANGE boolean not null, \
                        SET_DT date default now()::date not null \
                        );')

    def __del__(self):
        self.cursor.close()
        self.db.close()
