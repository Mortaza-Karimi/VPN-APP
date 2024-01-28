# check all users internet used
# and despite from fund

import sqlite3


users_con = sqlite3.connect('users.sqlite',check_same_thread=False)
users_cur = users_con.cursor()
xui_con = sqlite3.connect('x-ui.sqlite',check_same_thread=False)
xui_cur = xui_con.cursor()

users = users_cur.execute("SELECT * FROM users").fetchall()
clients = xui_cur.execute("SELECT * FROM client_traffics").fetchall()
user = None
client = None
for i in users:
    for j in clients:
        print(j)
        if j[3]==i[0]:
            client = j
            break
    user = i
    used = (int(j[5])+int(j[4]))/(1024*1024*1024)
    fund = int(user[4])-((used)*2000)
    users_cur.execute(f"UPDATE users SET fund='{fund}' WHERE username='{user[0]}'")
    users_con.commit()