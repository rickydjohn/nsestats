#!/usr/bin/env python

import sys
from os import getcwd
sys.path.append(getcwd() + "/pymodules")
import plotter
from json import dumps
from flask import Flask, render_template, request, session, redirect, flash, url_for
from nseLookup import MapFormat
from finLogin import Connector
import datetime

app = Flask(__name__)
app.secret_key = "SSBjYW4gZG8gYWxsIHRoaW5ncyB0aHJvdWdoIENocmlzdCB3aG8gc3RyZW5ndGhlbnMgbWUK"

cacher = {}
ListOfOption = dumps([i[-1] for i in MapFormat().Stocks()])

def authenticate(request):
    connector  = Connector("127.0.0.1", "root", "megh", "fintech")
    return connector.checkLogin(request.form["username"], request.form["password"])


def generate_graph(search="NIFTY"):
    try:
        stock = search.upper()
        data = MapFormat(offset=8)
        data.url = stock
        if stock in cacher and (datetime.datetime.now() - cacher[stock]["time"]).seconds < 60:
            return cacher[stock]
        else:
            stock_data = data.parse()
            if data == None:
                return None
            oi_chg_graph, oi_chg_raw = data.oi_change_graph()
            oi_graph, oi_raw = data.oi_numbers()
            max_pain = data.max_pain()
            grapher = [{"graph": oi_chg_graph, "raw": oi_chg_raw}, {"graph": oi_graph, "raw": oi_raw}, {"graph": max_pain}]
            cacher[stock] = {"data": grapher, "time": datetime.datetime.now(), "info": stock_data["info"]}
            return cacher[stock]
    except:
        return None


#=============================================================

@app.route("/secret")
def secret():
    a = plotter.get_data("nifty")
    return render_template('secret.html', data=a)
    

@app.route("/user")
def user():
    if "username" in session:

        return render_template('user.html', logged_in=True, user=session["f_name"], graph_data = generate_graph())
    else:
        flash("You are currently not logged in")
        return redirect(url_for("landing"))

@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username")
        flash("You have been logged out successfully")
        return redirect(url_for("landing"))
    else:
        flash("You are currently not logged in")
        return redirect(url_for("landing"))

@app.route("/register", methods=["POST"])
def register():
    pass

@app.route("/login", methods=["POST"])
@app.route("/home")
@app.route("/search", methods=["POST"])
def home():
    if request.method =="POST"  and request.path == "/login":
        data = authenticate(request)
        if data["Authenticated"] == True and data["state"] == "enabled":
            session["username"] = data["email"]
            session["f_name"] = data["f_name"]
            return render_template('home.html', logged_in=True, user=session["f_name"], graph_data = generate_graph())
        elif data["Authenticated"] == True and data["state"] != "enabled":
            flash("Error: Please complete email address verification")
            return redirect(url_for(("landing")))
        else:
            flash("Error: Incorrect username/password")
            return redirect(url_for(("landing")))
    elif request.method == "POST" and request.path == "/search":
        if "username" in session:
            graph_data = generate_graph(request.form["search"])
            if not graph_data:
                flash("Error: "+ request.form["search"] + " is not a valid search parameter")
                return redirect(url_for(("landing")))
            else:
                return render_template('home.html', logged_in=True, user=session["f_name"], graph_data = generate_graph(request.form["search"]))
        else:
            flash("Error: You are not currently logged in")
            return redirect(url_for(("landing")))
    else:
        if "username" in session:
            return render_template('home.html', logged_in=True, user=session["f_name"], graph_data = generate_graph())
        else:
            flash("Error: You are not currently logged in")
            return redirect(url_for(("landing")))

@app.route('/')
def landing():
    if "username" in session:
        return redirect(url_for("home"))
    else:
        return render_template('main.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=True)
