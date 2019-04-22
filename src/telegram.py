import requests

MAX_TIME_TO_REPEAT = 100


class Telegram:

    def __init__(self, SSL_CERT, TOKEN):
        for i in range(MAX_TIME_TO_REPEAT):
            self.__URL = "https://api.telegram.org/bot" + TOKEN + "/"
            answer = requests.post(self.__URL + "setWebhook",
                                   data={'url': "https://217.73.88.161:8443/tgbot/" + TOKEN},
                                   files={'certificate': open(SSL_CERT, 'rb')})
            if answer.ok:
                break

    def send_message(self, chat_id, message):
        for i in range(MAX_TIME_TO_REPEAT):
            answer = requests.post(self.__URL + "sendMessage",
                                   data={'chat_id': str(chat_id), 'text': str(message)})
            if answer.ok:
                break
