from flask import Flask, render_template, url_for, request, session, redirect
from gdastudio import *
from html import escape
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)


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

        # ZESZLEM Z BLEDU
        query = """SELECT 
                        [id]
                        ,[username]
                        ,[email]
                        ,[password_hash]
                FROM [MICROBLOG].[MICRO].[users]
                WHERE %s = ? and password_hash = ? """
        # ====================================================
        results = cursor.execute(
            query % ("username"), (user,  passwd)).fetchone()

        try:
            if results:

                session["LOGGED_IN"] = "You_Are_Logged"
                print("You are logged in")
                conn.close()
                return redirect(url_for('loggedin', results=results))
            else:
                raise ValueError("Bad login or password")

        except Exception as err:
            print(err)

    return render_template("loginForm.html")


@app.route('/loggedin/<results>', methods=["GET", "POST"])
def loggedin(results):
    if session.get("LOGGED_IN"):
        print(results)
        return render_template("loginPanel.html", results=results)
    else:
        return render_template("loginForm.html")


if __name__ == '__main__':
    app.run()
