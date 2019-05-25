import threading
import time
import datetime


class SendAlarmClock(threading.Thread):

    def __init__(self, tg_bot, data_base):
        threading.Thread.__init__(self)
        self.send_tg_message = tg_bot.send_message
        self.cursor = data_base.data_base.cursor()
        self.work = True

    def run(self):
        while self.work:
            utc_time_now = datetime.datetime.utcnow()
            self.cursor.execute("Select text, chat_id "
                                "from alarmclock inner join client on alarmclock.login = client.login "
                                "where time <= %(time)s", {'time': utc_time_now})

            for text, chat_id in self.cursor:
                send_thread = threading.Thread(target=self.send_tg_message, args=(chat_id, text))
                send_thread.start()

            self.cursor.execute("Delete from alarmclock "
                                "where time <= %(time)s", {'time': utc_time_now})

            time_now = time.time()
            minute_in_hour = 60
            delta = minute_in_hour - int(time_now) % minute_in_hour
            for _ in range(delta):
                if not self.work:
                    break
                time.sleep(1)
