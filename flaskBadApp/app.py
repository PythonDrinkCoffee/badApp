from flask import Flask, render_template, url_for, request
from gdastudio import *
from html import escape

app = Flask(__name__)


query = """SELECT 
                [id]
                ,[username]
                ,[email]
                ,[password_hash]
        FROM [MICROBLOG].[MICRO].[%s]
        WHERE username = ? and password_hash = ? """


@app.route("/", methods=['GET'])
def index():
    return render_template('base.html')


@app.route("/loginForm", methods=["POST", "GET"])
def loginForm():
    if request.method == 'POST' and request.form.get("loginForm") == 'submit':
        user = request.form.get("user")
        passwd = request.form.get("pass")
        sql = JSONFile('config', 'sql')
        conn = SQLConn(sql).conn
        cursor = conn.cursor()
        results = cursor.execute(query % ("users"), [user, passwd]).fetchone()
        try:
            if results:
                print("You are logged in")
            else:
                raise ValueError("Bad login or password")
        except Exception as err:
            print(err)

        conn.close()
    return render_template("loginForm.html")


if __name__ == '__main__':
    app.run()
