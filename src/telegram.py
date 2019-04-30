import requests
import time

MAX_TIME_TO_REPEAT = 100


class Telegram:

    def __init__(self, SSL_CERT, TOKEN, TELEGRAM_PATH, HOST, PORT):

        if PORT not in [80, 88, 443, 8443]:
            ValueError("Incorrect port, might be in [80, 88, 443, 8443]")

        for i in range(MAX_TIME_TO_REPEAT):
            self.__URL = "https://api.telegram.org/bot" + TOKEN + "/"
            answer = requests.post(self.__URL + "setWebhook",
                                   data={'url': "https://" + str(HOST) + ":" + str(PORT) + "/tgbot/" + TELEGRAM_PATH},
                                   files={'certificate': open(SSL_CERT, 'rb')})
            if answer.ok:
                break
            time.sleep(1)

    def SendMessage(self, chat_id, message):
        for i in range(MAX_TIME_TO_REPEAT):
            answer = requests.post(self.__URL + "sendMessage",
                                   data={'chat_id': str(chat_id), 'text': str(message)})
            if answer.ok:
                break
            time.sleep(1)

    def Close(self):
        for i in range(MAX_TIME_TO_REPEAT):
            answer = requests.post(self.__URL + "setWebhook")

            if answer.ok:
                break
            time.sleep(1)
