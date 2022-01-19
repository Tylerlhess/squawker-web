from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template, send_file, abort
from flask.json import jsonify
from markupsafe import escape
from web_profile import Profile
from utils import *
from web_message import Message
from market import Listing
import os
from credentials import GOOGLE_OAUTH2_SECRET, GOOGLE_OAUTH2_CLIENTID, SITE_SECRET_KEY
from dbconn import Conn
from squawker_errors import *
from flask_bootstrap import Bootstrap
from forms import *
from serverside import rvn, TEST_WALLET_ADDRESS, WALLET_ADDRESS
import logging
from flask_wtf.csrf import CSRFProtect
from web_account import Account

#csrf = CSRFProtect()

app = Flask(__name__)


app.secret_key = SITE_SECRET_KEY
#csrf.init_app(app)

site_url = 'https://squawker.app'

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
handler2 = logging.FileHandler(filename='squawker.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)


@app.route("/", methods=['GET'])
def index():
    logger.info(f'Session started with {session}')
    latest_msg = find_latest_messages(asset="SQUAWKER")
    messages = []
    for m in latest_msg:
        try:
            messages.append(Message(m).html())
        except:
            pass
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


@app.route('/login_google')  # login with google
def logintogoogle():
    google = OAuth2Session(GOOGLE_OAUTH2_CLIENTID, redirect_uri=site_url + "/callback_google", scope=google_scope)

    google_authorization_url, gstate = google.authorization_url(google_authorization_base_url, access_type="offline", prompt="select_account")
    session['oauth_state'] = gstate
    return redirect(google_authorization_url)


@app.route('/callback_google')  # login routing with google
def callbackfromgoogle():
    google = OAuth2Session(GOOGLE_OAUTH2_CLIENTID, redirect_uri=site_url + "/callback_google", state=session['oauth_state'])

    google_token = google.fetch_token(google_token_url, client_secret=GOOGLE_OAUTH2_SECRET,
                                      authorization_response=request.url)

    session['oauth_token'] = google_token
    logger.info(f"google callback {session['oauth_token']}")

    google = OAuth2Session(GOOGLE_OAUTH2_CLIENTID, token=session['oauth_token'])
    google_user = google.get("https://www.googleapis.com/oauth2/v1/userinfo").json()

    email = google_user["email"]
    session['email'] = email
    logger.info(f"session email = {session['email']} in {session}")
    try:
        conn = Conn()
        result = conn.get_address(email)
        logger.info(f'get address returned {result}')
        session['address'] = result['p2sh_address']
        session['phash'], session['ptime'] = result['profile_hash'], result['profile_timestamp']
        if session['phash'] is not None:
            return redirect(url_for('index'))
        else:
            try:
                if conn.fix_profile(session['address']):
                    return redirect(url_for('index'))
                else:
                    return render_template("setup_profile.html.jinja", form=tRegister())
            except Exception as e:
                logger.info(f'{type(e)} {e} returned.')
                return abort('404')

    except NotRegistered:
        return render_template("setup_account.html.jinja", form=tRegister())
    except NoProfile:
        # Has current session top pass account
        return render_template("setup_profile.html.jinja", form=tRegister())
    except Exception as e:
        logger.info(f'Raised exception {type(e)} : {e} session is set to {session}')
        return redirect('/')

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
    session.clear()
    return redirect("squawker.app/")


@app.route('/send_message_file')
def senddownload(filepath=None):
    if filepath is None:
        abort(400)
    try:
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        abort(400)


@app.route("/new_message", methods=['GET', 'POST'])
def new_message():
    form = SendKaw()
    logger.info(f"/new_message Form values = {form.data}")
    if request.method == 'POST' and form.validate():
        account = Account(session["email"])
        tx_id, x, hash = account.send_kaw(form.data["kaw"])
        logger.info(f"/new_message tx id = {tx_id} and hash = {hash}")
        return redirect('squawker.app/')

    return render_template('new_message.html.jinja', form=form)


@app.route('/edit_profile_test', methods=['GET', 'POST'])
def edit_profile_test():
    try:
        form = EditProfile()
        logger.info(f"Form values = {form.data}")
        if request.method == 'POST' and form.validate():
            conn = Conn()
            session_data = conn.submit_tprofile((session["email"], form.data), {})
            for key in session_data['profile']['keys']:
                logger.info(f"updating session {key} with session_data key {session_data}")
                session[key] = session_data[key]
            Account(session['email']).update_profile(profile_dict=session_data)
            return redirect('/')
        if not session["profile"]:


        return render_template('edit_profile.html.jinja', form=form)
    except KeyError:
        if not session['email']:
            return redirect('https://squawker.app/login_google')
        if not session["profile"]:
            return render_template('edit_profile.html.jinja', form=form)
        return redirect('https://squawker.app')

@app.route('/market', methods=['GET','POST'])
def market():
    form = MarketAsset()
    logger.info(f"market form data is {form.data['asset']}")
    if request.method == 'POST' and form.validate():
        latest_listings = find_latest_flags(form.data["asset"], satoshis=20000000)
        listings = []
        for l in latest_listings:
            try:
                listings.append(Listing(l).html())
            except:
                pass
        return render_template("market.html.jinja", listings=listings, form=form)
    else:
        latest_listings = find_latest_flags("SQUAWKER", satoshis=20000000)
        listings = []
        for l in latest_listings:
            try:
                listings.append(Listing(l).html())
            except:
                pass
        return render_template("market.html.jinja", listings=listings, form=form)

