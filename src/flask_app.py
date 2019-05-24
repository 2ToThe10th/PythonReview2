import hashlib
import secrets
import string
import datetime
from flask import Flask, request, session, render_template, redirect, url_for


class FlaskApp:
    def __init__(self, TELEGRAM_PATH, HOST, PORT, SSL_CERT, SSL_KEY, SECRET_KEY, db, tg_bot):
        app = Flask(__name__)

        @app.route('/tgbot/' + TELEGRAM_PATH, methods=['POST'])
        def TelegramUpdate():
            json_data = request.get_json()

            try:
                text = str(json_data['message']['text'])
                chat_id = str(json_data['message']['from']['id'])
            except Exception:
                print(json_data)
                return ('', 204)

            if text == '/start':
                tg_bot.SendMessage(chat_id=chat_id, message="Hello. If you want to sign up write /reg and then your login and your timezone. For example:\n/reg Aleksandr Creator +3")
            elif len(text) >= 4 and text[:4] == '/reg':
                row_data = text[4:].split(' ')
                data = []
                for part in row_data:
                    if part != '':
                        data.append(part)
                if len(data) < 2:
                    tg_bot.SendMessage(chat_id=chat_id, message="Incorrect parameters. Sign Up might be like this:\n/reg Pasha -5")
                else:
                    login = str(' '.join(data[:-1]))

                    if len(login) > 40:
                        tg_bot.SendMessage(chat_id=chat_id, message="Login must be no more than 40 symbols")
                        return '', 204

                    try:
                        gmt = int(data[-1])
                        if gmt < -12 or gmt > 14:
                            raise ValueError('Incorrect gmt')
                    except Exception:
                        tg_bot.SendMessage(chat_id=chat_id, message="timezone might be a number between -12 and 14")
                        return '', 204

                    db.cursor.execute("Select * from CLIENT where login = %s", (login,))

                    if db.cursor.rowcount:
                        tg_bot.SendMessage(chat_id=chat_id, message="Login is already used. Please, choose other")
                    else:
                        db.cursor.execute("Select * from CLIENT where chat_id = %s", (chat_id,))
                        if db.cursor.rowcount:
                            tg_bot.SendMessage(chat_id=chat_id,
                                               message="You are already sign up from this telegram account. Please, choose other or use your already registered account")
                        else:
                            password = ''.join(
                                secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in
                                range(10))
                            password_sha256 = hashlib.sha256(password.encode())
                            db.cursor.execute("Insert into CLIENT (login, password, is_time_password, gmt, chat_id) " +
                                              "values(%(login)s , %(password)s, True, %(gmt)s, %(chat_id)s);",
                                              {'login': login, 'password': password_sha256.hexdigest(), 'gmt': gmt,
                                               'chat_id': chat_id})
                            tg_bot.SendMessage(chat_id=chat_id, message="Your login: " + login + "\n" +
                                               "Your time password: " + password + "\nYou can login and change "
                                               "your password on https://" + str(HOST) + ":" + str(PORT))
            else:
                tg_bot.SendMessage(chat_id=chat_id, message="Sorry, but it is not a command. I have only 2 command:"
                                                            " /start and /reg [name] [gmt]")

            return '', 204

        def AlreadyLogin(our_session):
            if our_session.get('session') is None:
                return None

            db.cursor.execute(
                'Select a.login from LOGIN_SESSION a inner join CLIENT b on a.login = b.login where session = %(session)s and is_time_password = False;',
                {'session': our_session['session']})
            if db.cursor.rowcount:
                return db.cursor.fetchone()[0]

            return None

        def RedirectIfNone(our_session):
            if our_session.get('session') is not None:
                db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s',
                                  {'session': our_session['session']})
                if db.cursor.rowcount:
                    return redirect(url_for('ChangePassword'))

            return redirect(url_for('Login'))

        @app.route('/', methods=['GET'])
        @app.route('/index', methods=['GET'])
        def Index():
            login = AlreadyLogin(session)
            if login is None:
                return RedirectIfNone(session)

            db.cursor.execute(
                'Select time, text, gmt, id from alarmclock inner join client on alarmclock.login = client.login where client.login = %(login)s order by time',
                {'login': login})

            alarm_clocks = []

            for alarm_clock in db.cursor.fetchall():
                alarm_clocks.append(
                    {'time': (alarm_clock[0] + datetime.timedelta(hours=int(alarm_clock[2]))).ctime(), 'text': alarm_clock[1], 'id': alarm_clock[3]})

            return render_template('index.html', login=login, alarm_clocks=alarm_clocks)

        @app.route('/create_alarm_clock', methods=['GET', 'POST'])
        def CreateAlarmClock():
            if request.method == 'GET':
                login = AlreadyLogin(session)
                if login is None:
                    return RedirectIfNone(session)

                db.cursor.execute("Select gmt from client where login = %(login)s", {'login': login})
                return render_template('create_alarm_clock.html', login=login,
                                       time=(datetime.datetime.utcnow() + datetime.timedelta(hours=db.cursor.fetchone()[0])))

            login = AlreadyLogin(session)
            if login is None:
                return RedirectIfNone(session)
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
                    db.cursor.execute("Select gmt from client where login = %(login)s", {'login': login})
                    time -= datetime.timedelta(hours=db.cursor.fetchone()[0])

                    if time <= datetime.datetime.utcnow():
                        db.cursor.execute("Select gmt from client where login = %(login)s", {'login': login})
                        return render_template('create_alarm_clock.html', login=login,
                                               time=(datetime.datetime.utcnow() + datetime.timedelta(hours=db.cursor.fetchone()[0])),
                                               error="Time might be in future")

                    db.cursor.execute('Insert into ALARMCLOCK(id, login, time, text) \
                                values(default, %(login)s, %(time)s, %(text)s)',
                                      {'login': login, 'time': time, 'text': text})

                    return redirect(url_for('Index'))
                except Exception:
                    db.cursor.execute("Select gmt from client where login = %(login)s", {'login': login})
                    return render_template('create_alarm_clock.html', login=login,
                                           time=(datetime.datetime.utcnow() + datetime.timedelta(hours=db.cursor.fetchone()[0])),
                                           error="Incorrect data")
            else:
                db.cursor.execute("Select gmt from client where login = %(login)s", {'login': login})
                return render_template('create_alarm_clock.html', login=login,
                                       time=(datetime.datetime.utcnow() + datetime.timedelta(hours=db.cursor.fetchone()[0])),
                                       error="Please, fill all fields")

        @app.route('/remove_alarm_clock/<alarm_clock_id>', methods=['GET'])
        def RemoveAlarmClock(alarm_clock_id):
            login = AlreadyLogin(session)
            if login is None:
                return RedirectIfNone(session)

            db.cursor.execute('Select id from alarmclock where login = %(login)s and id = %(id)s',
                              {'id': str(alarm_clock_id), 'login': login})

            if db.cursor.rowcount:
                db.cursor.execute('Delete from alarmclock where id = %(id)s', {'id': str(alarm_clock_id)})

            return redirect(url_for('Index'))

        @app.route('/login', methods=['GET', 'POST'])
        def Login():
            if request.method == 'GET':
                if AlreadyLogin(session) is not None:
                    return redirect(url_for('Index'))

                if session.get('session') is not None:
                    db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s',
                                      {'session': session['session']})
                    if db.cursor.rowcount:
                        return redirect(url_for('ChangePassword'))

                    return render_template('login.html', incorrect_login=False)

            if request.form.get('login') is not None and request.form.get('password') is not None:
                login = request.form['login']
                password = request.form['password']
                password_sha256 = hashlib.sha256(password.encode()).hexdigest()

                db.cursor.execute('Select login from client where login = %(login)s and password = %(password)s',
                                  {'login': login, 'password': password_sha256})

                if db.cursor.rowcount != 1:
                    return render_template('login.html', incorrect_login=True)

                while True:
                    try:
                        new_session = ''.join(
                            secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in
                            range(50))
                        db.cursor.execute(
                            'Insert into login_session(login, session, set_dt) values(%(login)s, %(session)s, default)',
                            {'login': login, 'session': new_session})
                        break
                    except Exception:
                        pass

                session['session'] = new_session
                session['session'] = new_session

                return redirect(url_for('Index'))

            return render_template('login.html', incorrect_login=True)

        @app.route('/logout', methods=['GET'])
        def Logout():
            if session.get('session') is not None:
                db.cursor.execute('delete from LOGIN_SESSION where session = %(session)s',
                                  {'session': session['session']})
            session['session'] = ""
            return redirect(url_for('Login'))

        @app.route('/change_password', methods=['GET', 'POST'])
        def ChangePassword():
            if request.method == 'GET':
                login = ""
                if session.get('session') is not None:
                    db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s',
                                      {'session': session['session']})
                    if db.cursor.rowcount:
                        login = db.cursor.fetchone()[0]

                return render_template('change_password.html', login=login)

            if request.form.get('login') is not None and \
               request.form.get('current_password') is not None and \
               request.form.get('new_password') is not None and \
               request.form.get('retype_new_password') is not None:

                login = request.form.get('login')
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                retype_new_password = request.form.get('retype_new_password')
                if new_password != retype_new_password:
                    login = ""
                    if session.get('session') is not None:
                        db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s',
                                          {'session': session['session']})
                        if db.cursor.rowcount:
                            login = db.cursor.fetchone()[0]
                    return render_template('change_password.html', login=login,
                                           error="New password is not equal to retype new password")

                cur_password_sha256 = hashlib.sha256(current_password.encode()).hexdigest()
                db.cursor.execute(
                    'Select gmt, chat_id from client where login = %(login)s and password = %(password)s',
                    {'login': login, 'password': cur_password_sha256})
                if db.cursor.rowcount:
                    db.cursor.execute('Delete from login_session where login = %(login)s', {'login': login})
                    new_password_sha256 = hashlib.sha256(new_password.encode()).hexdigest()
                    db.cursor.execute(
                        'Update client set password = %(password)s, is_time_password = False where login = %(login)s',
                        {'password': new_password_sha256, 'login': login})

                    while True:
                        try:
                            new_session = ''.join(
                                secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for
                                _ in range(50))
                            db.cursor.execute(
                                'Insert into login_session(login, session, set_dt) values(%(login)s, %(session)s, default)',
                                {'login': login, 'session': new_session})
                            break
                        except Exception:
                            pass

                    session['session'] = new_session

                    return redirect(url_for('Index'))

                login = ""
                if session.get('session') is not None:
                    db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s',
                                      {'session': session['session']})
                    if db.cursor.rowcount:
                        login = db.cursor.fetchone()[0]

                return render_template('change_password.html', login=login,
                                       error="Incorrect login/current password")

            login = ""
            if session.get('session') is not None:
                db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s',
                                  {'session': session['session']})
                if db.cursor.rowcount:
                    login = db.cursor.fetchone()[0]
            return render_template('change_password.html', login=login, error="Please, fill all fields")

        app.secret_key = SECRET_KEY
        app.run(host="0.0.0.0", port=int(PORT), ssl_context=(SSL_CERT, SSL_KEY), debug=False)
