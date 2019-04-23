import telegram
import flask_app

TOKEN = "749160029:AAFuIWuEjGMMLv7X66vMGch1u3ZCqP1RLtk"
SSL_CERT = "cert.pem"
SSL_KEY = "key.pem"

tg_bot = telegram.Telegram(SSL_CERT, TOKEN)

tg_bot.send_message(391332114, "Hello u too))")
flask_app = flask_app.FlaskApp(TOKEN)
