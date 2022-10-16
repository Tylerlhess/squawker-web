from ServerEssentials.credentials1 import DBUSER, DBNAME, DBPASS
import psycopg2
import logging
from Utils.squawker_errors import NotRegistered, NoProfile, AlreadyRegistered
from psycopg2.extras import DictCursor

logger = logging.getLogger('squawker_db')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_db.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawker.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)


class Conn:
    def __init__(self):
        self._conn = psycopg2.connect(f"dbname={DBNAME} user={DBUSER} password='{DBPASS}'")

    def get_address_test(self, email):
        logger.info(f"Failed to find {email} in prod checking testnet")
        tsql = "SELECT personal_address, p2sh_address, multisig_redeem_script, profile_hash, profile_timestamp FROM TUSERS where email = %s;"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(tsql, (email,))
            result = cur.fetchone()
            logger.info(f"{result} returned from {tsql}")
        if result:
            result_dict = dict()
            for x in ["personal_address", "p2sh_address", "multisig_redeem_script", "profile_hash",
                      "profile_timestamp"]:
                result_dict[x] = result[x]
            return result_dict
        else:
            raise NotRegistered(email)

    def get_address(self, email):
        try:
            sql = "SELECT personal_address, p2sh_address, multisig_redeem_script, profile_hash, profile_timestamp FROM USERS where email = %s;"
            with self._conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, (email,))
                result = cur.fetchone()
                logger.info(f"{result} returned from {sql}")
            if result:
                result_dict = dict()
                for x in ["personal_address", "p2sh_address", "multisig_redeem_script", "profile_hash", "profile_timestamp"]:
                    result_dict[x] = result[x]
                return result_dict
            else:
                raise NotRegistered(email)
        except:
            raise NotRegistered(email)

    def get_profile_data(self, address):
        sql = "SELECT profile FROM PROFILES where p2sh_address = %s"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, (address,))
            result = cur.fetchone()
            logger.info(f"{result} returned from {sql}, {address}")
        if result:
            return result[0]
        else:
            raise NoProfile(address)

    def fix_profile(self, address):
        sql = "SELECT profile FROM Profiles where p2sh_address = %s"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, (address,))
            result = cur.fetchone()[0]
            try:
                logger.info(f"{result}")
                if result["profile_ipfs_hash"]:
                    repair_sql = "UPDATE users set profile_hash = %s WHERE p2sh_address = %s"
                    cur.execute(repair_sql, (
                        str(result["profile_ipfs_hash"]), address))
                    repair_result = cur.fetchone()
                    repair_sql = "UPDATE users set profile_timestamp = %s WHERE p2sh_address = %s"
                    cur.execute(repair_sql, (
                        str(result["profile_timestamp"]), address))
                    repair_result = cur.fetchone()
                    return True
                else:
                    logger.info(f"{result} doesn't have a profile hash?")
                    raise NoProfile(address)
                return False
            except Exception as e:
                logger.info(f'{type(e)} {e} returned.')
                return False

    def submit_registration(self, form):
        sql = "INSERT INTO USERS (email, personal_address, p2sh_address, multisig_redeem_script) VALUES (%s, %s, %s, %s);"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, form)
            self._conn.commit()

    def submit_tregistration(self, tform):
        sql = "SELECT * FROM TUSERS where email = %s;"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, (tform[0],))
            result = cur.fetchone()
        if not result:
            tsql = "INSERT INTO TUSERS (email, personal_address, p2sh_address, multisig_redeem_script) VALUES (%s, %s, %s, %s);"
            with self._conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(tsql, tform)
                self._conn.commit()
            return True
        else:
            raise AlreadyRegistered(f"{tform[0]} already has an address of {result[0]['personal_address']} and p2sh of {result[0]['p2sh_address']}")

    def submit_tprofile(self, tform, profile):
        tsql = "SELECT * FROM TUSERS where email = %s"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(tsql, (tform[0],))
            result = cur.fetchone()
        if not result:
            raise NotRegistered(f"{tform[0]} has no address in our database.")
        else:
            #get old profile
            logger.info(f"Logging submit_tprofile result {result}")
            tsql = "SELECT * FROM PROFILES where p2sh_address = %s"
            with self._conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(tsql, [result['p2sh_address'],])
                pro_result = cur.fetchone()
            try:
                pro = dict()
                for key in pro_result['profile']['keys']:
                    pro[key] = pro_result['profile'][key]
                pro['keys'] = pro_result['profile']['keys']
                merged_profile = self.update_profile(pro, tform)
                return pro
            except:
                try:
                    raise NoProfile(f"pro result = {pro_result}")
                except NameError:
                    raise NotRegistered(f"{tform[0]} has no address in our database.")

    def build_tprofile(self, email):
        tsql = "SELECT profile_json from TUSERS where email = %s"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(tsql, (email,))
            result = cur.fetchone()[0]
        result_dict = dict()
        for x in ["p2sh_address", "profile"]:
            result_dict[x] = result[x]

        return result_dict

    def get_kaws(self, address=None):
        if address:
            sql = "select address, contents, timestamp, txid from kaw where address = %s order by timestamp desc;"
            with self._conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, (address,))
                return [dict(zip(["sender", "text", "timestamp", "txid"], result)) for result in cur.fetchall()]

        sql = "select address, contents, timestamp, txid from kaw order by timestamp desc;"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql)
            return [dict(zip(["sender", "text", "timestamp", "txid"], result)) for result in cur.fetchall()]

    def get_kaw(self, txid):
        try:
            sql = "select address, contents, timestamp, txid from kaw where txid = %s;"
            with self._conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, (txid,))
                return [dict(zip(["sender", "text", "timestamp", "txid"], cur.fetchall()[0]))]
        except IndexError:
            sql = "select address, contents, timestamp, txid from reply where txid = %s;"
            with self._conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, (txid,))
                return [dict(zip(["sender", "text", "timestamp", "txid"], cur.fetchall()[0]))]

    def get_profiles(self):
        sql = "select address, name, picture from (select address, name, picture, row_number() over (partition by address order by timestamp desc) as row_number from profile) temp where row_number = 1;"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql)
            return [dict(zip(["address", "name", "picture"], result)) for result in cur.fetchall()]

    def get_profile(self, address):
        sql = "select address, name, picture, ipfs_hash from (select address, name, picture, ipfs_hash, row_number() over (partition by address order by timestamp desc) as row_number from profile) temp where row_number = 1 and address = %s;"
        try:
            with self._conn.cursor() as cur:
                cur.execute(sql, (str(address), ))
                res = cur.fetchall()
                logger.info(f"result of query is {res}")
                return dict(zip(["address", "name", "profile_picture", "ipfs_hash"], res[0]))
        except:
            with self._conn.cursor() as cur:
                cur.execute(sql, (address, ))
                try:
                    logger.info(cur.fetchall())
                except:
                    pass

    def get_blogs(self):
        sql = "select address, support_address, article_title, article_version, article, ipfs_hash, timestamp, txid from (select address, \
        support_address, article_title, article_version, article, ipfs_hash, timestamp, txid, row_number() over (partition by support_address, \
        article_title order by timestamp desc) as row_number from blog) temp where row_number=1;"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql)
            return [dict(zip(["address", "support_address", "article_title", "article_version", "article", "ipfs_hash", "timestamp", "txid"], result)) for result in cur.fetchall()]

    def get_blog(self, address, ipfs_hash):
        sql = "select address, support_address, article_title, article_version, article, ipfs_hash, timestamp, txid from (select address, \
           support_address, article_title, article_version, article, ipfs_hash, timestamp, txid, row_number() over (partition by support_address, \
           article_title order by timestamp desc) as row_number from blog) \
           temp where row_number=1 and address = %s and ipfs_hash =%s;"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, (address, ipfs_hash))
            return dict(zip(["address", "support_address", "article_title", "article_version", "article", "ipfs_hash",
                             "timestamp", "txid"], cur.fetchall()[0]))

    def get_blog_for_reply(self, txid):
        sql = "select address, support_address, article_title, article_version, article, ipfs_hash, timestamp, txid \
        from blog where txid = %s;"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, (txid, ))
            return dict(zip(["address", "support_address", "article_title", "article_version", "article", "ipfs_hash", "timestamp", "txid"], cur.fetchall()[0]))

    def get_replies(self, txid):
        sql = "select address, contents, timestamp, txid from reply where reply_to_txid = %s order by timestamp desc;"
        with self._conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, (txid,))
            return [dict(zip(["sender", "text", "timestamp", "txid"], result)) for result in cur.fetchall()]