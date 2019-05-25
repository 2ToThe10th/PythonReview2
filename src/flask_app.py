import hashlib
import secrets
import string
import datetime
from flask import Flask, request, session, render_template, redirect, url_for


class FlaskApp:
    def __init__(self, telegram_path, host, port, ssl_cert, ssl_key, secret_key, db, tg_bot):
        app = Flask(__name__)

        def register_new_user(chat_id, text):

            length_of_command = 4
            row_data = text[length_of_command:].split(' ')
            data = []
            for part in row_data:
                if part != '':
                    data.append(part)

            minimum_words_required = 2
            if len(data) < minimum_words_required:
                tg_bot.send_message(chat_id=chat_id,
                                    message="Incorrect parameters. Sign Up might be like this:\n/reg Pasha -5")
            else:
                user_login = str(' '.join(data[:-1]))

                max_user_login_length = 40
                if len(user_login) > max_user_login_length:
                    tg_bot.send_message(chat_id=chat_id, message="Login must be no more than 40 symbols")
                    return

                try:
                    gmt = int(data[-1])
                    min_possible_gmt = -12
                    max_possible_gmt = 14
                    if gmt < min_possible_gmt or gmt > max_possible_gmt:
                        raise ValueError('Incorrect gmt')
                except Exception:
                    tg_bot.send_message(chat_id=chat_id, message="timezone might be a number between -12 and 14")
                    return

                db.cursor.execute("Select * from CLIENT where login = %s", (user_login,))

                if db.cursor.rowcount:
                    tg_bot.send_message(chat_id=chat_id, message="Login is already used. Please, choose other")
                else:
                    db.cursor.execute("Select * from CLIENT where chat_id = %s", (chat_id,))
                    if db.cursor.rowcount:
                        tg_bot.send_message(chat_id=chat_id,
                                            message="You are already sign up from this telegram account. "
                                                    "Please, choose other or use your already registered account")
                    else:
                        password_length = 10
                        password = ''.join(
                            secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in
                            range(password_length))
                        password_sha256 = hashlib.sha256(password.encode())
                        db.cursor.execute("Insert into CLIENT (login, password, is_time_password, gmt, chat_id) "
                                          "values(%(login)s , %(password)s, True, %(gmt)s, %(chat_id)s);",
                                          {'login': user_login, 'password': password_sha256.hexdigest(), 'gmt': gmt,
                                           'chat_id': chat_id})
                        tg_bot.send_message(chat_id=chat_id,
                                            message="Your login: " + user_login + "\n" + "Your time "
                                            "password: " + password + "\nYou can login and change "
                                            "your password on https://" + str(host) + ":" + str(port))

        @app.route('/tgbot/' + telegram_path, methods=['POST'])
        def telegram_update():
            json_data = request.get_json()

            try:
                text = str(json_data['message']['text'])
                chat_id = str(json_data['message']['from']['id'])
            except Exception:
                print(json_data)
                return '', 204

            length_of_command_reg_with_space = 4
            if text == '/start':
                tg_bot.send_message(chat_id=chat_id,
                                    message="Hello. If you want to sign up write /reg and then your "
                                            "login and your timezone. For example:\n/reg Aleksandr Creator +3")
            elif len(text) >= length_of_command_reg_with_space and text[:length_of_command_reg_with_space] == '/reg':
                register_new_user(chat_id, text)
            else:
                tg_bot.send_message(chat_id=chat_id, message="Sorry, but it is not a command. I have only 2 command:"
                                                             " /start and /reg [name] [gmt]")

            return '', 204

        def already_login(our_session):
            if our_session.get('session') is None:
                return None

            db.cursor.execute("Select a.login "
                              "from LOGIN_SESSION a inner join CLIENT b on a.login = b.login "
                              "where session = %(session)s and is_time_password = False;",
                              {'session': our_session['session']})
            if db.cursor.rowcount:
                return db.cursor.fetchone()[0]

            return None

        def redirect_if_none(our_session):
            if our_session.get('session') is not None:
                db.cursor.execute("Select login from LOGIN_SESSION "
                                  "where session = %(session)s",
                                  {'session': our_session['session']})
                if db.cursor.rowcount:
                    return redirect(url_for('change_password'))

            return redirect(url_for('login'))

        @app.route('/', methods=['GET'])
        @app.route('/index', methods=['GET'])
        def index():
            login = already_login(session)
            if login is None:
                return redirect_if_none(session)

            db.cursor.execute(
                "Select time, text, gmt, id "
                "from alarmclock inner join client on alarmclock.login = client.login "
                "where client.login = %(login)s order by time",
                {'login': login})

            alarm_clocks = []

            for alarm_clock in db.cursor.fetchall():
                alarm_clocks.append(
                    {'time': (alarm_clock[0] + datetime.timedelta(hours=int(alarm_clock[2]))).ctime(),
                     'text': alarm_clock[1], 'id': alarm_clock[3]})

            return render_template('index.html', login=login, alarm_clocks=alarm_clocks)

        @app.route('/create_alarm_clock', methods=['GET', 'POST'])
        def create_alarm_clock():
            if request.method == 'GET':
                user_login = already_login(session)
                if user_login is None:
                    return redirect_if_none(session)

                db.cursor.execute("Select gmt "
                                  "from client where login = %(login)s",
                                  {'login': user_login})
                return render_template('create_alarm_clock.html', login=user_login,
                                       time=(datetime.datetime.utcnow() + datetime.timedelta(
                                           hours=db.cursor.fetchone()[0])))

            user_login = already_login(session)
            if user_login is None:
                return redirect_if_none(session)
            if request.form.get('year') is not None and \
               request.form.get('month') is not None and \
               request.form.get('day') is not None and \
               request.form.get('hour') is not None and \
               request.form.get('minute') is not None and \
               request.form.get('text') is not None:

                try:
                    year = int(request.form['year'])
                    month = int(request.form['month'])
                    day = int(request.form['day'])
                    hour = int(request.form['hour'])
                    minute = int(request.form['minute'])
                    text = request.form['text']

                    if text == '':
                        raise ValueError()

                    time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
                    db.cursor.execute("Select gmt from client where login = %(login)s", {'login': user_login})
                    time -= datetime.timedelta(hours=db.cursor.fetchone()[0])

                    if time <= datetime.datetime.utcnow():
                        db.cursor.execute("Select gmt "
                                          "from client where login = %(login)s",
                                          {'login': user_login})
                        return render_template('create_alarm_clock.html', login=user_login,
                                               time=(datetime.datetime.utcnow() + datetime.timedelta(hours=db.cursor.fetchone()[0])),
                                               error="Time might be in future")

                    db.cursor.execute("Insert into ALARMCLOCK(id, login, time, text) "
                                      "values(default, %(login)s, %(time)s, %(text)s)",
                                      {'login': user_login, 'time': time, 'text': text})

                    return redirect(url_for('index'))
                except Exception:
                    db.cursor.execute("Select gmt from client "
                                      "where login = %(login)s",
                                      {'login': user_login})
                    return render_template('create_alarm_clock.html', login=user_login,
                                           time=(datetime.datetime.utcnow() + datetime.timedelta(hours=db.cursor.fetchone()[0])),
                                           error="Incorrect data")
            else:
                db.cursor.execute("Select gmt from client "
                                  "where login = %(login)s",
                                  {'login': user_login})
                return render_template('create_alarm_clock.html', login=user_login,
                                       time=(datetime.datetime.utcnow() + datetime.timedelta(
                                           hours=db.cursor.fetchone()[0])),
                                       error="Please, fill all fields")

        @app.route('/remove_alarm_clock/<alarm_clock_id>', methods=['GET'])
        def remove_alarm_clock(alarm_clock_id):
            user_login = already_login(session)
            if user_login is None:
                return redirect_if_none(session)

            db.cursor.execute('Select id from alarmclock '
                              'where login = %(login)s and id = %(id)s',
                              {'id': str(alarm_clock_id), 'login': user_login})

            if db.cursor.rowcount:
                db.cursor.execute('Delete from alarmclock where id = %(id)s',
                                  {'id': str(alarm_clock_id)})

            return redirect(url_for('index'))

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'GET':
                if already_login(session) is not None:
                    return redirect(url_for('index'))

                if session.get('session') is not None:
                    db.cursor.execute("Select login from LOGIN_SESSION "
                                      "where session = %(session)s",
                                      {'session': session['session']})
                    if db.cursor.rowcount:
                        return redirect(url_for('change_password'))

                    return render_template('login.html', incorrect_login=False)

            if request.form.get('login') is not None and request.form.get('password') is not None:
                login = request.form['login']
                password = request.form['password']
                password_sha256 = hashlib.sha256(password.encode()).hexdigest()

                db.cursor.execute("Select login from client "
                                  "where login = %(login)s and password = %(password)s",
                                  {'login': login, 'password': password_sha256})

                if db.cursor.rowcount != 1:
                    return render_template('login.html', incorrect_login=True)

                while True:
                    try:
                        session_length = 50
                        new_session = ''.join(
                            secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in
                            range(session_length))
                        db.cursor.execute(
                            "Insert into login_session(login, session, set_dt) "
                            "values(%(login)s, %(session)s, default)",
                            {'login': login, 'session': new_session})
                        break
                    except Exception:
                        pass

                session['session'] = new_session
                session['session'] = new_session

                return redirect(url_for('index'))

            return render_template('login.html', incorrect_login=True)

        @app.route('/logout', methods=['GET'])
        def logout():
            if session.get('session') is not None:
                db.cursor.execute('delete from LOGIN_SESSION '
                                  'where session = %(session)s',
                                  {'session': session['session']})
            session['session'] = ""
            return redirect(url_for('login'))

        @app.route('/change_password', methods=['GET', 'POST'])
        def change_password():
            if request.method == 'GET':
                user_login = ""
                if session.get('session') is not None:
                    db.cursor.execute('Select login from LOGIN_SESSION '
                                      'where session = %(session)s',
                                      {'session': session['session']})
                    if db.cursor.rowcount:
                        user_login = db.cursor.fetchone()[0]

                return render_template('change_password.html', login=user_login)

            if request.form.get('login') is not None and \
               request.form.get('current_password') is not None and \
               request.form.get('new_password') is not None and \
               request.form.get('retype_new_password') is not None:

                user_login = request.form.get('login')
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                retype_new_password = request.form.get('retype_new_password')
                if new_password != retype_new_password:
                    user_login = ""
                    if session.get('session') is not None:
                        db.cursor.execute("Select login from LOGIN_SESSION "
                                          "where session = %(session)s",
                                          {'session': session['session']})
                        if db.cursor.rowcount:
                            user_login = db.cursor.fetchone()[0]
                    return render_template('change_password.html', login=user_login,
                                           error="New password is not equal to retype new password")

                cur_password_sha256 = hashlib.sha256(current_password.encode()).hexdigest()
                db.cursor.execute(
                    "Select gmt, chat_id from client "
                    "where login = %(login)s and password = %(password)s",
                    {'login': user_login, 'password': cur_password_sha256})
                if db.cursor.rowcount:
                    db.cursor.execute('Delete from login_session where login = %(login)s', {'login': user_login})
                    new_password_sha256 = hashlib.sha256(new_password.encode()).hexdigest()
                    db.cursor.execute(
                        "Update client "
                        "set password = %(password)s, is_time_password = False "
                        "where login = %(login)s",
                        {'password': new_password_sha256, 'login': user_login})

                    while True:
                        try:
                            session_length = 50
                            new_session = ''.join(
                                secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for
                                _ in range(session_length))
                            db.cursor.execute(
                                "Insert into login_session(login, session, set_dt) "
                                "values(%(login)s, %(session)s, default)",
                                {'login': user_login, 'session': new_session})
                            break
                        except Exception:
                            pass

                    session['session'] = new_session

                    return redirect(url_for('index'))

                user_login = ""
                if session.get('session') is not None:
                    db.cursor.execute("Select login from LOGIN_SESSION "
                                      "where session = %(session)s",
                                      {'session': session['session']})
                    if db.cursor.rowcount:
                        user_login = db.cursor.fetchone()[0]

                return render_template('change_password.html', login=user_login,
                                       error="Incorrect login/current password")

            user_login = ""
            if session.get('session') is not None:
                db.cursor.execute("Select login from LOGIN_SESSION "
                                  "where session = %(session)s",
                                  {'session': session['session']})
                if db.cursor.rowcount:
                    user_login = db.cursor.fetchone()[0]
            return render_template('change_password.html', login=user_login, error="Please, fill all fields")

        app.secret_key = secret_key
        app.run(host="0.0.0.0", port=int(port), ssl_context=(ssl_cert, ssl_key), debug=False)
