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
            day_from = datetime.date.today() - datetime.timedelta(days=7)
            self.cursor.execute('Delete from login_session where set_dt <= %(date)s', {'date': day_from})
            time_to_awake = 60 * 60 * 24 - int(time.time()) % (60 * 60 * 24)
            for _ in range(time_to_awake):
                if not self.work:
                    break
                time.sleep(1)

    def close(self):
        self.work = False
        self.cursor.close()
        self.join()
