import time
import requests

MAX_TIME_TO_REPEAT = 100


class Telegram:

    def __init__(self, SSL_CERT, TOKEN, TELEGRAM_PATH, HOST, PORT):

        if PORT not in [80, 88, 443, 8443]:
            ValueError("Incorrect port, might be in [80, 88, 443, 8443]")

        for _ in range(MAX_TIME_TO_REPEAT):
            self.__url = "https://api.telegram.org/bot" + TOKEN + "/"
            answer = requests.post(self.__url + "setWebhook",
                                   data={'url': "https://" + str(HOST) + ":" + str(PORT) + "/tgbot/" + TELEGRAM_PATH},
                                   files={'certificate': open(SSL_CERT, 'rb')})
            if answer.ok:
                break
            time.sleep(1)

    def send_message(self, chat_id, message):
        for _ in range(MAX_TIME_TO_REPEAT):
            answer = requests.post(self.__url + "sendMessage",
                                   data={'chat_id': str(chat_id), 'text': str(message)})
            if answer.ok:
                break
            time.sleep(1)

    def close(self):
        for _ in range(MAX_TIME_TO_REPEAT):
            answer = requests.post(self.__url + "setWebhook")

            if answer.ok:
                break
            time.sleep(1)
