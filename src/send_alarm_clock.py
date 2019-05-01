import threading
import time
import datetime

class SendAlarmClock(threading.Thread):
    
    def __init__(self, tg_bot, db):
        threading.Thread.__init__(self)
        self.SendTgMessage = tg_bot.SendMessage
        self.cursor = db.db.cursor()
        self.work = True
        pass

    def run(self):
        while self.work:
            utc_time_now = datetime.datetime.utcnow()
            self.cursor.execute("Select text, chat_id from alarmclock inner join client on alarmclock.login = client.login where time <= %(time)s", {'time': utc_time_now})

            for text, chat_id in self.cursor:
                send_thread = threading.Thread(target=self.SendTgMessage, args=(chat_id, text))
                send_thread.start()

            self.cursor.execute("Delete from alarmclock where time <= %(time)s", {'time': utc_time_now})
            
            x = time.time()
            delta = 60 - int(x) % 60
            for i in range(delta):
                if not self.work:
                    break
                time.sleep(1)
            pass
