from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template, send_file, abort
from flask.json import jsonify
from markupsafe import escape
from profile import Profile
from squawker import *
from message import Message
import os
from credentials import GOOGLE_OAUTH2_SECRET, GOOGLE_OAUTH2_CLIENTID, SITE_SECRET_KEY
from dbconn import Conn
from squawker_errors import *
from flask_bootstrap import Bootstrap
from forms import *
from serverside import rvn, TEST_WALLET_ADDRESS, WALLET_ADDRESS
import logging
from flask_wtf.csrf import CSRFProtect

#csrf = CSRFProtect()

app = Flask(__name__)


app.secret_key = SITE_SECRET_KEY
#csrf.init_app(app)

site_url = 'https://squawker.badguyty.com'

google_redirect_uri = 'https://squawker.badguyty.com/callback'
google_authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
google_token_url = "https://www.googleapis.com/oauth2/v4/token"
google_scope = [
    "https://www.googleapis.com/auth/userinfo.email"
]

logger = logging.getLogger('squawker_app')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_app.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


@app.route("/")
def index():
    latest_msg = find_latest_messages(asset="SQUAWKER")
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


@app.route('/login-google')  # login with google
def logintogoogle():
    google = OAuth2Session(GOOGLE_OAUTH2_CLIENTID, redirect_uri=site_url + "/callback-google", scope=google_scope)

    google_authorization_url, gstate = google.authorization_url(google_authorization_base_url, access_type="offline", prompt="select_account")
    session['oauth_state'] = gstate
    return redirect(google_authorization_url)


@app.route('/callback-google')  # login routing with google
def callbackfromgoogle():
    google = OAuth2Session(GOOGLE_OAUTH2_CLIENTID, redirect_uri=site_url + "/callback-google", state=session['oauth_state'])

    google_token = google.fetch_token(google_token_url, client_secret=GOOGLE_OAUTH2_SECRET,
                                      authorization_response=request.url)

    session['oauth_token'] = google_token

    google = OAuth2Session(GOOGLE_OAUTH2_CLIENTID, token=session['oauth_token'])
    google_user = google.get("https://www.googleapis.com/oauth2/v1/userinfo").json()

    email = google_user["email"]
    session['email'] = email
    try:
        conn = Conn()
        session['address'] = conn.get_address(email)
        session['phash'], session['ptime'] = conn.get_profile(email)
    except NotRegistered:
        return render_template("setup_account.html.jinja", form=tRegister())
    except NoProfile:
        # Has current session top pass account
        return render_template("setup_profile.html.jinja")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        multisig = rvn.createmultisig('{[1, "[\"{form.address}\", \"{WALLET_ADDRESS}\"]"]}')
        form.p2sh_address = multisig["address"]
        form.multisig_redeem_script = multisig["redeemScript"]
        conn = Conn()
        conn.submit_registration(form)
        return redirect('/')
    return render_template('setup_account.html.jinja', form=form)


@app.route('/register_test', methods=['GET', 'POST'])
def tregister():
    form = tRegister()
    logger.info(f"Form validation results = {form.validate()}")
    logger.info(f"Form values = {form.data}")
    if request.method == 'POST' and form.validate():
        keys = [form.data["address"], TEST_WALLET_ADDRESS]
        multisig = rvn.createmultisig(1, keys)["result"]
        conn = Conn()
        conn.submit_tregistration((session["email"], form.data["address"], multisig["address"], multisig["redeemScript"]))
        return render_template('edit_profile.html.jinja', form=EditProfile())
    return render_template('setup_account.html.jinja', form=form)


@app.route("/logout")
def logout():
    return redirect("/")


@app.route('/send-message-file')
def senddownload(filepath=None):
    if filepath is None:
        abort(400)
    try:
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        abort(400)


@app.route("/new-message")
def new_message():
    return None


@app.route('/edit_profile_test')
def edit_profile_test():
    form = EditProfile()
    logger.info((f"Form values = {form.data}"))
    if request.method == 'POST' and form.validate():
        conn = Conn()
        session_data = conn.submit_tprofile((session["email"], form.data))
        for key in session_data:
            session[key] = session_data[key]
        return redirect('/')
    return render_template('edit_profile.html.jinja', form=form)


