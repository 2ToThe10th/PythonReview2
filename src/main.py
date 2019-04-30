import telegram
import flask_app
import postgresql
import secrets
import string
import send_alarm_clock
import time

TELEGRAM_PATH = ''.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(50))

db = postgresql.Postgresql(DB_NAME, DB_USER, PASSWORD)
tg_bot = telegram.Telegram(SSL_CERT, TOKEN, TELEGRAM_PATH, HOST, PORT)
send_alarm_clock = send_alarm_clock.SendAlarmClock(tg_bot, db)
send_alarm_clock.start()
flask_app = flask_app.FlaskApp(TOKEN, TELEGRAM_PATH, HOST, PORT, SSL_CERT, SSL_KEY, SECRET_KEY, db, tg_bot)

print("\nShutdown started. It may take a minute")
send_alarm_clock.work = False
send_alarm_clock.join()
db.Close()
tg_bot.Close()
print("Done")
