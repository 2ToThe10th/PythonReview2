from flask import *
from threading import Thread
import hashlib
import secrets
import string

class FlaskApp:
    def __init__(self, TOKEN, TELEGRAM_PATH, HOST, PORT, SSL_CERT, SSL_KEY, SECRET_KEY, db, tg_bot):
        app = Flask(__name__)

        @app.route('/tgbot/' + TELEGRAM_PATH, methods=['POST'])
        def telegram_update():
            
            json_data = request.get_json()
                
            try:
                text = str(json_data['message']['text'])
                chat_id = str(json_data['message']['from']['id'])
            except:
                print(json_data)
                return ('', 204)
            
            if text == '/start':
                tg_bot.send_message(chat_id=chat_id, message="Hello. If you want to sign up write /reg and then " +
                                                             "your login and your timezone. For example:\n/reg Aleksandr Creator +3")
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
                        if gmt < -12 or gmt > 14:
                            raise ValueError('Incorrect gmt') 
                    except:
                        tg_bot.send_message(chat_id=chat_id, message="timezone might be a number between -12 and 14")
                        return ('', 204)
                                       
                    db.cursor.execute("Select * from CLIENT where login = %s", (login,))
                    
                    if db.cursor.rowcount:
                        tg_bot.send_message(chat_id=chat_id, message="Login is already used. Please, choose other")
                    else:
                        db.cursor.execute("Select * from CLIENT where chat_id = %s", (chat_id,))
                        if db.cursor.rowcount:
                            tg_bot.send_message(chat_id=chat_id, message="You are already sign up from this telegram account. Please, choose other or use your already registered account")
                        else:
                            password = ''.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(10))
                            passwdsha256 = hashlib.sha256(password.encode())
                            db.cursor.execute("Insert into CLIENT (login, password, is_time_password, gmt, chat_id) " + \
                                              "values(%(login)s , %(passwd)s, True, %(gmt)s, %(chat_id)s);",
                                              {'login': login, 'passwd': passwdsha256.hexdigest(), 'gmt': gmt, 'chat_id': chat_id})
                            tg_bot.send_message(chat_id=chat_id, message="Your login: " + login + "\n" +
                                                             "Your time password: " + password + "\n" +
                                                             "You can login and change your password " +
                                                             "on https://" + str(HOST) + ":" + str(PORT))

            return ('', 204)


        def AlreadyLogin(session):
            if session.get('session') is None:
                return None
            else:
                db.cursor.execute('Select a.login from LOGIN_SESSION a inner join CLIENT b on a.login = b.login where session = %(session)s and is_time_password = False;', 
                                  {'session': session['session']})
                if db.cursor.rowcount:
                    return db.cursor.fetchone()[0]
                else:
                    return None

        def redirect_if_None(session):
            if session.get('session') is not None:
                db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s', {'session': session['session']})
                if db.cursor.rowcount:
                    return redirect('change_password')
            
            return redirect('login')


        @app.route('/',  methods=['GET'])
        @app.route('/index',  methods=['GET'])
        def index():
            login = AlreadyLogin(session)
            if login is None:
                return redirect_if_None(session)
            else:
                return login
    
        @app.route('/create_alarm', methods=['GET', 'POST'])
        def create_alarm():
            if request.method == 'GET':
                login = AlreadyLogin(session)
                if login is None:
                    return redirect_if_None(session)
                else:
                    return render_template('create_alarm.html', login=login)

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'GET':
                if AlreadyLogin(session) is not None:
                    return redirect('index')
                else:
                    if session.get('session') is not None:
                        db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s', {'session': session['session']})
                        if db.cursor.rowcount:
                            return redirect('change_password')
                    
                    return render_template('login.html', incorrect_login=False)
            else:
                if request.form.get('login') is not None and request.form.get('password') is not None:
                    login = request.form['login']
                    password = request.form['password']
                    passwdsha256 = hashlib.sha256(password.encode()).hexdigest()

                    db.cursor.execute('Select login from client where login = %(login)s and password = %(passwd)s',
                                      {'login': login, 'passwd': passwdsha256})
                    
                    if db.cursor.rowcount != 1:
                        return render_template('login.html', incorrect_login=True) 
                   
                    while True:
                        try:
                            new_session = ''.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(50))
                            db.cursor.execute('Insert into login_session(login, session, set_dt) values(%(login)s, %(session)s, default)',
                                              {'login': login, 'session': new_session})
                            break
                        except Exception:
                            pass
                    
                    session['session'] = new_session

                    return redirect(url_for('index'))
                else:
                    return render_template('login.html', incorrect_login=True)

        @app.route('/logout', methods=['GET'])
        def logout():
            db.cursor.execute('delete from LOGIN_SESSION where session = %(session)s',
                              {'session': session['session']})
            session['session'] = ""
            return redirect(url_for("login"))

        @app.route('/change_password', methods=['GET', 'POST'])
        def ChangePassword():
            if request.method == 'GET':
                login = ""
                if session.get('session') is not None:
                    db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s', {'session': session['session']})
                    if db.cursor.rowcount:
                        login = db.cursor.fetchone()[0]

                return render_template('change_password.html', login=login)
            else:
                if request.form.get('login') is not None and request.form.get('current_password') is not None and request.form.get('new_password') is not None and request.form.get('retype_new_password') is not None:
                    login = request.form.get('login')
                    current_passwd = request.form.get('current_password')
                    new_passwd = request.form.get('new_password')
                    retype_new_passwd = request.form.get('retype_new_password')
                    if new_passwd != retype_new_passwd:
                        login = ""
                        if session.get('session') is not None:
                            db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s', {'session': session['session']})
                            if db.cursor.rowcount:
                                login = db.cursor.fetchone()[0]
                        return render_template('change_password.html', login=login, error="New password is not equal to retype new password")

                    cur_passwd_sha256 = hashlib.sha256(current_passwd.encode()).hexdigest()
                    db.cursor.execute('Select gmt, chat_id from client where login = %(login)s and password = %(passwd)s', {'login': login, 'passwd': cur_passwd_sha256})
                    if db.cursor.rowcount:
                        db.cursor.execute('Delete from login_session where login = %(login)s', {'login': login})
                        new_passwd_sha256 = hashlib.sha256(new_passwd.encode()).hexdigest()
                        db.cursor.execute('Update client set password = %(passwd)s, is_time_password = False where login = %(login)s', 
                                   {'passwd': new_passwd_sha256, 'login': login})
                        
                        while True:
                            try:
                                new_session = ''.join(secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(50))
                                db.cursor.execute('Insert into login_session(login, session, set_dt) values(%(login)s, %(session)s, default)',
                                                  {'login': login, 'session': new_session})
                                break
                            except Exception as e:
                                pass

                        session['session'] = new_session

                        return redirect(url_for('index'))
                    else:
                        login = ""
                        if session.get('session') is not None:
                            db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s', {'session': session['session']})
                            if db.cursor.rowcount:
                                login = db.cursor.fetchone()[0]

                        return render_template('change_password.html', login=login, error="Incorrect login/current password")
                else:
                    login = ""
                    if session.get('session') is not None:
                        db.cursor.execute('Select login from LOGIN_SESSION where session = %(session)s', {'session': session['session']})
                        if db.cursor.rowcount:
                            login = db.cursor.fetchone()[0]
                    return render_template('change_password.html', login=login, error = "Please, fill all fields")

        app.secret_key = SECRET_KEY
        app.run(host="0.0.0.0", port=int(PORT), ssl_context=(SSL_CERT, SSL_KEY), debug=False) 
