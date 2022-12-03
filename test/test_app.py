import pytest
from test.conftest import client


def test_index(client):
    response = client.get()
    assert b"Your life, your content&mdash;own it." in response.data

# def test_user(rvn_address):
# def test_profile(rvn_address):
# def test_message(message_address):
# def test_login():
# def test_logout():
# # def test_market():
# def test_AET():
# # def test_KAW():
# def test_reply(reply_txid):
# # def test_publish():
def test_blogs(client):
    response = client.get("/blog_posts")
# def test_article(address, article_hash):
# def test_kaws():
# def test_sent(txid):
# def test_like(txid, sender):
# def test_get_rss(address):
#
