class Config:
    def __init__(self, config_json):
        self.token = config_json['TOKEN']
        self.ssl_cert = config_json['SSL_CERT']
        self.ssl_key = config_json['SSL_KEY']
        self.host = config_json['HOST']
        self.port = int(config_json['PORT'])
        self.db_name = config_json['DB_NAME']
        self.db_user = config_json['DB_USER']
        self.password = config_json['PASSWORD']
        self.secret_key = config_json['SECRET_KEY']
