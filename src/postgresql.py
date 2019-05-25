import psycopg2


class PostgreSQL:
    def __init__(self, db_name, db_user, password):
        self.data_base = psycopg2.connect(dbname=db_name, user=db_user,
                                          password=password, host='localhost')
        self.data_base.autocommit = True

        self.cursor = self.data_base.cursor()
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
                        SET_DT date default now()::date not null \
                        );')

    def close(self):
        self.cursor.close()
        self.data_base.close()
