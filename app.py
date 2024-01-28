from flask import Flask, jsonify, request, Response, redirect, url_for, session, abort,render_template
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user 
import sqlite3, uuid, json, base64
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import config

app = Flask(__name__)

app.config.update(
    SECRET_KEY = 'secret_xxx'
)

limiter = Limiter(get_remote_address, app=app)


users_con = sqlite3.connect('users.sqlite',check_same_thread=False)
users_cur = users_con.cursor()
xui_con = sqlite3.connect('x-ui.sqlite',check_same_thread=False)
xui_cur = xui_con.cursor()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        return "%d" % (self.id)


# create some users with ids 1 to 20       
user = User(0)

 
# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password']        
        if username == config.PANEL_USERNAME and password == config.PANEL_PASSWORD:
            login_user(user)
            return redirect('/')
        else:
            return abort(401)
    else:
        html = """Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')"""
        return render_template("login.html") 


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)
    

@app.route('/')
@login_required
def home():
    users_num = len(json.loads(xui_cur.execute("SELECT settings FROM inbounds WHERE port=1080").fetchall()[0][0])["clients"])
    income = 0
    users = users_cur.execute("SELECT * FROM users").fetchall()
    print(users)
    for user in users:
        income+=user[4]
    result = {"users_num":users_num,'income':income,"users":users}
    return render_template('index.html',result=result)

 


@app.route("/users/login")
def user_login():
    data = request.args
    username = data["username"]
    token = check_user(username=username)
    response = {"username":username,"token":token}
    return jsonify(response),200

@app.route("/users/signup")
def user_signup():
    data = request.args
    username = data["username"]
    password = data["password"]
    token = str(uuid.uuid4())
    res = create_user(username=username,password=password,token=token)
    return jsonify({"status":res}),200

@app.route("/users/fundup")
def user_fundup():
    data = request.args
    pay_token = data["pay_token"]
    user_token = data["user_token"]
    fundup_price = int(data["fundup_price"])
    users_cur.execute(f"UPDATE users SET fundup_status='nok',fundup_token='{pay_token}',fundup_price={fundup_price} WHERE token='{user_token}'")
    users_con.commit()
    return jsonify({"msg":'ok'}),200

@app.route("/users/fundup/confirm")
def user_fundup_confirm():
    response = {}

    data = request.args
    authority = data["Authority"]
    status = data["Status"]

    if status=="ok":
        funds = users_cur.execute(f"SELECT fund,fundup_price,fund_history FROM users WHERE fundup_token='{authority}'").fetchall()[0]
        print(funds)
        fund = funds[0]
        fundup_price = funds[1]
        fund_history = funds[2]
        new_fund = int(fund)+int(fundup_price)
        new_fund_history = int(fund_history)+int(fundup_price)
        print(new_fund)
        user = users_cur.execute(f'UPDATE users SET fundup_status = "ok" , fund = {new_fund} , fund_history = {new_fund_history} WHERE fundup_token="{authority}"')
        users_con.commit()
        response = {"status":"ok"}
    else:
        response = {"status":"nok"}

    return jsonify(response),200

@app.route("/users/get_configs")
def user_get_configs():
    data = request.args
    user_token = data["user_token"]

    user_email = users_cur.execute(f"SELECT * FROM users WHERE token='{user_token}'").fetchall()[0][0]

    clients = json.loads(xui_cur.execute("SELECT settings FROM inbounds WHERE port=1080").fetchall()[0][0])["clients"]

    user_id=None
    config = None
    for user in clients:
        if user['email']==user_email:
            user_id = user["id"]
            config = '{'+f'"add":"morteza.devdecode.shop","aid":"0","host":"taaghche.com","id":"{user_id}","net":"tcp","path":"/","port":"1080","ps":"{user_email}","scy":"auto","sni":"","tls":"","type":"http","v":"2"'+'}'
            break
    
    
    return base64.b64encode(config.encode('ascii')).decode('ascii')

def create_user(username,password,token):
    users_cur.execute(f"INSERT INTO users VALUES ('{username}','{password}','{token}',5000,0,'ok','',0)")
    users_con.commit()

    user = users_cur.execute(f"SELECT * FROM users WHERE username='{username}'")

    if user.fetchall()[0]:
        return "ok"
    else:
        return "nok"

def check_user(username):
    res = users_cur.execute(f"SELECT * FROM users WHERE username='{username}'")
    return res.fetchall()[0][2]

if __name__ == "__main__":
    app.run("0.0.0.0",5000,debug=True)