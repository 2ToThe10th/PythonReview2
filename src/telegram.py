import requests


class Telegram:
    def __init__(self, SSL_CERT, TOKEN):
        self.__URL = "https://api.telegram.org/bot" + TOKEN + "/"
        requests.post(self.__URL + "setWebhook",
                      data={'url': "https://217.73.88.161:8443/tgbot/" + TOKEN},
                      files={'certificate': open(SSL_CERT, 'rb')})

    def send_message(self, chat_id, message):
        requests.post(self.__URL + "sendMessage",
                      data={'chat_id': str(chat_id), 'message': str(message)})
