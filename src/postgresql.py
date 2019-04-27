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
                        PASSWORD varchar(128) not null, \
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

    def __del__(self):
        self.cursor.close()
        self.db.close()
