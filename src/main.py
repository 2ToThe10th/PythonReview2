import telegram
import flask_app
import postgresql

TOKEN = "749160029:AAFuIWuEjGMMLv7X66vMGch1u3ZCqP1RLtk"
SSL_CERT = "cert.pem"
SSL_KEY = "key.pem"
HOST = "217.73.88.161"
PORT = 8443
DB_NAME = "alarmclock"
DB_USER = "alarmclock"
PASSWORD = "alarmclockpasswd"
SECRET_KEY = "rdghea1jbMRzBQrgYqwCop6JQz0A2VHCjnpVJSkLxX6oYWzpH4"

db = postgresql.Postgresql(DB_NAME, DB_USER, PASSWORD)
tg_bot = telegram.Telegram(SSL_CERT, TOKEN, HOST, PORT)
flask_app = flask_app.FlaskApp(TOKEN, HOST, PORT, SSL_CERT, SSL_KEY, SECRET_KEY, db, tg_bot)

del(db)
del(tg_bot)
