from json_profile import Profile
from Utils.utils import get_logger
from dbconn import Conn
from xml.sax.saxutils import escape
from email.utils import formatdate

logger = get_logger("squawker_rss")


def rss(address):
    this_profile = Profile(address)
    conn = Conn()
    feed_txt = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>{escape(this_profile.name)}</title>
<link>https://squawker.app/rss/{escape(this_profile.address)}</link>
<description>{escape(this_profile.name)} - {escape(this_profile.address)}</description>
"""
    for message in conn.get_kaws(address=this_profile.address):
        logger.info(message)
        appendage = f"""<item>
<title>{formatdate(message["timestamp"])}</title>
<link>"https://squawker.app/message/{escape(message["txid"])}</link>
<guid>{escape(message["txid"])}</guid>
<pubDate>{formatdate(message["timestamp"])}</pubDate>
<description>{escape(message["text"])}</description>
</item>
"""
        logger.info(f"adding {appendage}")
        feed_txt += appendage
    feed_txt += f"""</channel>
</rss>"""
    return feed_txt
