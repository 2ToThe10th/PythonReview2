import secrets
import string
import argparse
import json
import telegram
import flask_app
import postgresql
import trash_cleaner
import send_alarm_clock
import server_config


def read_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="config file")
    args = vars(parser.parse_args())

    try:
        with open(args["config_file"], "r") as config_file:
            config_text = config_file.readlines()
        config_json = json.loads(''.join(config_text))

        config = server_config.Config(config_json)

    except Exception:
        raise ValueError("Bad config file")

    return config


def main():

    config = read_config()

    config.telegram_path = ''.join(secrets.choice(
        string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(50))

    data_base = postgresql.PostgreSQL(config.db_name, config.db_user, config.password)
    tg_bot = telegram.Telegram(config.ssl_cert, config.token, config.telegram_path, config.host, config.port)
    send_alarm_clocks = send_alarm_clock.SendAlarmClock(tg_bot, data_base)
    send_alarm_clocks.start()
    trash_from_db_cleaner = trash_cleaner.TrashCleaner(data_base)
    trash_from_db_cleaner.start()
    flask_app.FlaskApp(config.telegram_path, config.host, config.port, config.ssl_cert, config.ssl_key, config.secret_key, data_base, tg_bot)

    print("\nShutdown started. It may take a minute")
    send_alarm_clocks.work = False
    trash_from_db_cleaner.close()
    send_alarm_clocks.join()
    send_alarm_clocks.cursor.close()
    data_base.close()
    tg_bot.close()
    print("Done")


if __name__ == "__main__":
    main()
