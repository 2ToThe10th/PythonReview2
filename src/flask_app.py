from flask import *


class FlaskApp:
    def __init__(self, TOKEN, SSL_CERT, SSL_KEY):
        app = Flask(__name__)

        @app.route('/tgbot/' + TOKEN + '/', methods=['POST'])
        def telegram_update():
            print(request.get_data())
            return None
