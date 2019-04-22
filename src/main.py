import telegram

TOKEN = "749160029:AAFuIWuEjGMMLv7X66vMGch1u3ZCqP1RLtk"
SSL_CERT = "cert.pem"
SSL_KEY = "key.pem"

tg_bot = telegram.Telegram(SSL_CERT, TOKEN)
