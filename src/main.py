import telegram
import flask_app

TOKEN = "749160029:AAFuIWuEjGMMLv7X66vMGch1u3ZCqP1RLtk"
SSL_CERT = "cert.pem"
SSL_KEY = "key.pem"
HOST = "217.73.88.161"
PORT = 8443

tg_bot = telegram.Telegram(SSL_CERT, TOKEN, HOST, PORT)

tg_bot.send_message(391332114, "Hello u too))")
flask_app = flask_app.FlaskApp(TOKEN, HOST, PORT, SSL_CERT, SSL_KEY)
