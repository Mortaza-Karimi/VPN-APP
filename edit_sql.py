import sqlite3,json

con = sqlite3.connect('users.sqlite')

cur = con.cursor()

# cur.execute("DROP TABLE users")
# cur.execute(f"UPDATE users SET fund_history=100000  WHERE username='mohammad'")
res = cur.execute("CREATE TABLE users (username , password , token , fund , fund_history , fundup_status , fundup_token, fundup_price)")
# res = cur.execute("""SELECT username FROM users WHERE username='mk'""")
# res = cur.execute("""INSERT INTO users VALUES ("father","mkmkmk","222",0,0)""")
# clients = cur.execute("SELECT settings FROM inbounds WHERE port=1080").fetchall()
# print(clients)
# print(res)

con.commit()