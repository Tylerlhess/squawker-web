import requests, json
from flask import Flask, request, redirect, session, url_for, render_template, send_file, abort
from utils import *
from market import Listing
from credentials import SITE_SECRET_KEY, site_url
from dbconn import Conn
from forms import *
import logging
from web_account import Account
from json_message import Message
from json_profile import Profile
from json_blog import Article
from squawker_errors import *
from json_rss import rss



app = Flask(__name__)


app.secret_key = SITE_SECRET_KEY

#site_url = 'https://squawker.app'

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
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    session["site_url"] = site_url
    logger.info(f'Session started with {session} in index')
    if "signstring" not in session:
        session["signstring"] = gen_signstring()
    conn = Conn()
    messages = [Message(msg).html() for msg in conn.get_kaws()]
    return render_template("front-page.html.jinja", base_url=site_url, messages=messages, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route("/user/<rvn_address>")
def user(rvn_address):
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    usr = Profile(rvn_address).html()
    #return str(usr)
    return render_template("user.html.jinja", profile=usr, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)

@app.route("/profile/<rvn_address>")
def profile(rvn_address):
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    usr = Profile(rvn_address).html()
    return render_template("profile.html.jinja", profile=usr, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)

@app.route("/message/<message_address>")
def message(message_address):
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    msg = Message(message_address)
    return str(msg)


@app.route('/login', methods=['POST', 'GET'])
def login():
    """The function to login"""
    session["site_url"] = site_url

    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()
    if "signstring" not in session:
        session["signstring"] = gen_signstring()

    if request.method == 'POST' and loginForm.validate():
        params = {'jsonRequest': json.dumps(loginForm.data)}
        url = 'http://127.0.0.1:8081/api/verify_sig'
        r = requests.post(url, params=params)
        logger.info(f"{r.text}, {r.status_code}")
        if "True" in r.text:
            session["site_url"] = site_url
            session["address"] = loginForm["address"]
            profile = Profile(str(session['address']))
            for atb in profile.__dict__:
                if atb == "picture":
                    session["profile_picture"] = profile.profile_picture
                elif atb == "name":
                    session["name"] = profile.name
                elif atb == "address":
                    pass
                else:
                    if "others" not in session:
                        session["others"] = dict()
                    if not callable(atb):
                        session["others"][atb] = profile.__dict__[atb]

        return redirect(site_url)

    return render_template("login_page.html.jinja", base_url=site_url, loginForm=loginForm, kawForm=kawForm, articleForm=articleForm, profile_form=proForm)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(site_url)


@app.route('/update_profile', methods=['GET', 'POST'])
def edit_profile():
    try:
        kawForm = SendKaw()
        articleForm = PublishArticle()
        proForm = EditProfile()
        loginForm = Login()

        logger.info(f"Form values = {form.data}")
        if request.method == 'POST' and form.validate():
            for key in session['profile']['keys']:
                logger.info(f"updating session {key} with session_data key {session_data}")
                session[key] = session_data[key]
            Account(session['email']).update_profile(profile_dict=session_data)
            return redirect(site_url)
        return render_template('edit_profile.html.jinja', base_url=site_url, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)
    except KeyError:
        return redirect(f'{site_url}/login')


@app.route('/market', methods=['GET','POST'])
def market():
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

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
        return render_template("market.html.jinja", listings=listings, form=form, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)
    else:
        latest_listings = find_latest_flags("SQUAWKER", satoshis=20000000)
        listings = []
        for l in latest_listings:
            try:
                listings.append(Listing(l).html())
            except:
                pass
        return render_template("market.html.jinja", listings=listings, form=form, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route('/AET', methods=['GET'])
def AET():
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    form = AETRedemption()
    return render_template("submit_AET_tag_redemption.html.jinja", base_url=site_url, form=form, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route('/KAW', methods=['GET'])
def KAW():
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    form = SendKaw()
    return render_template("submit_kaw.html.jinja", base_url=site_url, form=form, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route('/reply/<reply_txid>', methods=['GET'])
def reply(reply_txid):
    form = ReplyKaw()
    conn = Conn()
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    try:
        kaw = conn.get_kaw(reply_txid)
        logger.info(f"{kaw} is the kaw in reply")
        messages = [Message(msg).html() for msg in kaw]
    except:
        art = conn.get_blog_for_reply(reply_txid)
        art["sender"] = art["address"]
        art["text"] = art["article_title"]
        logger.info(f"{art} is the current article")
        messages = [Message(art).html()]
    return render_template("reply_to_kaw.html.jinja", base_url=site_url, form=form, messages=messages, reply_txid=reply_txid, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route('/publish', methods=['GET', 'POST'])
def publish():
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    form = PublishArticle()
    return render_template("submit_blog.html.jinja", base_url=site_url, form=form, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route("/blog_posts", methods=['GET'])
def blogs():
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    session["site_url"] = site_url
    logger.info(f'Session started with {session} in blog_posts')
    if "signstring" not in session:
        session["signstring"] = gen_signstring()
    conn = Conn()
    articles = [Article(blog["address"], blog["ipfs_hash"]).short_html() for blog in conn.get_blogs()]
    return render_template("index2.html.jinja", base_url=site_url, articles=articles, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route("/article/<address>/<article_hash>", methods=['GET'])
def article(address, article_hash):
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    art = Article(address, article_hash).html()
    session["site_url"] = site_url
    logger.info(f'Session started with {session} in article')
    if "signstring" not in session:
        session["signstring"] = gen_signstring()
    return render_template("article.html.jinja", base_url=site_url, article=art, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route("/kaws", methods=['GET'])
def kaws():
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    session["site_url"] = site_url
    logger.info(f'Session started with {session}')
    if "signstring" not in session:
        session["signstring"] = gen_signstring()
    conn = Conn()
    messages = [Message(msg).html() for msg in conn.get_kaws()]

    return render_template("view_kaws.html.jinja", base_url=site_url, messages=messages, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route("/sent/<txid>", methods=['GET'])
def sent(txid):
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    session["site_url"] = site_url
    logger.info(f'Session started with {session}')
    if "signstring" not in session:
        session["signstring"] = gen_signstring()
    conn = Conn()
    return render_template("followup.html.jinja", base_url=site_url, txid=txid, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)


@app.route("/like/<txid>/<sender>", methods=['GET'])
def like(txid, sender):
    kawForm = SendKaw()
    articleForm = PublishArticle()
    proForm = EditProfile()
    loginForm = Login()

    return render_template("like.html.jinja", base_url=site_url, txid=txid, sender=sender, kawForm=kawForm, articleForm=articleForm, profile_form=proForm, loginForm=loginForm)

@app.route("/rss/<address>")
def get_rss(address):
    return app.response_class(rss(address), mimetype='application/xml')