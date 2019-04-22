import requests


class Telegram:
    def __init__(self, SSL_CERT, TOKEN):
        self.__TOKEN = TOKEN
        requests.post("https://api.telegram.org/bot" + TOKEN + "/setWebhook",
                      data={'url': "https://217.73.88.161:8443/tgbot/" + TOKEN},
                      files={'certificate': open(SSL_CERT, 'rb')})
