import threading
import time
import datetime


class TrashCleaner(threading.Thread):
    def __init__(self, data_base):
        threading.Thread.__init__(self)
        self.cursor = data_base.data_base.cursor()
        self.work = True

    def run(self):
        while self.work:
            session_lifetime = 7
            day_from = datetime.date.today() - datetime.timedelta(days=session_lifetime)
            self.cursor.execute('Delete from login_session where set_dt <= %(date)s', {'date': day_from})
            second_in_hour = 60 * 60 * 24
            time_to_awake = second_in_hour - int(time.time()) % second_in_hour
            for _ in range(time_to_awake):
                if not self.work:
                    break
                time.sleep(1)

    def close(self):
        self.work = False
        self.cursor.close()
        self.join()
