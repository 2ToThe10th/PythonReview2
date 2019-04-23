from flask import *
from threading import Thread
import hashlib

class FlaskApp:
    def __init__(self, TOKEN, HOST, PORT, SSL_CERT, SSL_KEY, db, tg_bot):
        app = Flask(__name__)

        @app.route('/tgbot/' + TOKEN, methods=['POST'])
        def telegram_update():
            json_data = request.get_json()
            print(json_data)
            
            text = str(json_data['message']['text'])
            chat_id = str(json_data['message']['from']['id'])

            if text == '/start':
                tg_bot.send_message(chat_id=chat_id, message="Hello. If you want to sign up write /reg and then " +
                                                             "your login and your timezone. For example:\n/reg Sasha +3")
            elif len(text) >= 4 and text[:4] == '/reg':
                row_data = text[4:].split(' ')
                data = []
                for i in row_data:
                    if i != '':
                        data.append(i)
                if len(data) < 2:
                    tg_bot.send_message(chat_id=chat_id, message="Incorrect parameters. Sign Up might be like this:" +
                                                                 "\n/reg Pasha -5")
                else:
                    login = str(' '.join(data[:-1]))
                    
                    if len(login) > 40:
                        tg_bot.send_message(chat_id=chat_id, message="Login must be no more than 40 symbols")
                        return ('', 204)
                    
                    try:
                        gmt = int(data[-1])
                    except:
                        tg_bot.send_message(chat_id=chat_id, message="timezone might be a number")
                        return ('', 204)
                                       
                    db.cursor.execute("Select * from CLIENT where login = %s", (login,))
                    print(db.cursor.rowcount)
                    if db.cursor.rowcount:
                        tg_bot.send_message(chat_id=chat_id, message="Login is already used. Please, choose other")
                    else:
                        password = "nothing"
                        tg_bot.send_message(chat_id=chat_id, message="Your login: " + login + "\n" +
                                                             "Your time password: " + password + "\n" +
                                                             "You can login and change your password " +
                                                             "on https://" + str(HOST) + ":" + str(PORT))

            return ('', 204)

        @app.route('/', methods=['GET'])
        def index():
            return "Hello"

        app.run(host="0.0.0.0",port=int(PORT),ssl_context=(SSL_CERT, SSL_KEY)) 
