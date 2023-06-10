from flask import Flask, render_template, url_for, request, session, redirect
from gdastudio import *
from html import escape
import secrets
from datetime import datetime

app = Flask(__name__)
app.secret_key = "123123123"


@app.route("/", methods=['GET', "POST"])
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
                user_id = results[0]
                name = results[1]
                email = results[2]

                session["user_id"] = user_id
                session["name"] = name
                session["email"] = email

                conn.close()
                return redirect(url_for('loggedin'))
            else:
                raise ValueError("Bad login or password")

        except Exception as err:
            print(err)

    return render_template("loginForm.html")


@app.route("/profile/<string:user_id>/<string:name>/<string:email>", methods=["GET", "POST"])
def profile(user_id, name, email):
    if session.get("LOGGED_IN"):
        if str(user_id) == str(session.get("user_id")) and name == session.get("name") and email == session.get("email"):
            sql = JSONFile('config', 'sql')
            conn = SQLConn(sql).conn
            cursor = conn.cursor()

            if request.method == "POST" and request.form["post"] == "send":
                title = request.form["title"]
                body = request.form["message"]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_id = request.form["user_id"]

                cursor.execute("""
                INSERT INTO [MICROBLOG].[MICRO].[posts]
                (
                    [body]
                    ,[timestamp]
                    ,[user_id]
                    ,[title]
                )   VALUES (?,?,?,?)                
                """, [body, timestamp, user_id, title])
                cursor.commit()

                posts = cursor.execute("""
                SELECT [id]
                    ,[body]
                    ,[timestamp]
                    ,[user_id]
                    ,[title]
                FROM [MICROBLOG].[MICRO].[posts]
                """).fetchall()
                conn.close()
                return render_template("loginPanel.html", user_id=user_id, name=name, email=email, posts=posts)
            else:
                posts = cursor.execute("""
                SELECT [id]
                    ,[body]
                    ,[timestamp]
                    ,[user_id]
                    ,[title]
                FROM [MICROBLOG].[MICRO].[posts]
                """).fetchall()
                conn.close()
                return render_template("loginPanel.html", user_id=user_id, name=name, email=email, posts=posts)
        else:
            session.clear()
            return redirect(url_for("loginForm"))
    else:
        session.clear()
        return redirect(url_for("loginForm"))


@app.route('/loggedin', methods=["GET", "POST"])
def loggedin():
    if session.get("LOGGED_IN"):
        user_id = session.get("user_id")
        name = session.get("name")
        email = session.get("email")

        if name and email:
            return redirect(url_for("profile", user_id=user_id, name=name, email=email))
        else:
            session.clear()
            return redirect(url_for("loginForm"))
    else:
        session.clear()
        return redirect(url_for("loginForm"))


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("loginForm"))


if __name__ == '__main__':
    app.run()
