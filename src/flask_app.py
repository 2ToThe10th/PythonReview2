from flask import *


class FlaskApp:
    def __init__(self, TOKEN, HOST, PORT, SSL_CERT, SSL_KEY):
        app = Flask(__name__)

        @app.route('/tgbot/' + TOKEN + '/', methods=['POST'])
        def telegram_update():
            print(request.get_data())
            return None

        @app.route('/', methods=['GET'])
        def index():
            return "Hello"

        app.run(host=str(HOST), port=int(PORT), ssl_context=(SSL_CERT, SSL_KEY))
