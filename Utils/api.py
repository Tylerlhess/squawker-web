import logging
import requests


logger = logging.getLogger('squawker_utils')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_utils.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawker.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)

debug = 0


def messages():
    url = 'https://test.squawker.app/api?call=messages'
    r = requests.get(url)
    logger.info(f"requests returned {r.text}, {r.status_code}")
    return r.json()


def get_blogs():
    url = 'https://test.squawker.app/api?call=articles'
    r = requests.get(url)
    logger.info(f"requests returned {r.text}, {r.status_code}")
    return r.json()
