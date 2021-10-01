from flask import Flask, render_template
from markupsafe import escape
from profile import Profile
from squawker import *
from message import Message

app = Flask(__name__)

@app.route("/")
def index():
    latest_msg = find_latest_messages(asset="POLITICOIN")
    #return str(Message(latest[0]))
    messages = []
    for m in latest_msg:
        try:
            messages.append(Message(m).html())
        except:
            pass
    #return str(messages)
    return render_template("index.html.jinja", messages=messages)


@app.route("/user/<rvn_address>")
def user(rvn_address):
    usr = Profile(rvn_address).html()
    #return str(usr)
    return render_template("user.html.jinja", profile=usr)

@app.route("/profile/<rvn_address>")
def profile(rvn_address):
    usr = Profile(rvn_address).html()
    # #return str(usr)
    # page = ""
    # for atb in usr:
    #     page += str(atb) + str(usr[atb])
    return render_template("profile.html.jinja", profile=usr)

@app.route("/message/<message_address>")
def message(message_address):
    msg = Message(message_address)
    return str(msg)
