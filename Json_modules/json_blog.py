from Json_modules.json_profile import Profile
from Json_modules.json_message import Message
from Utils import squawker_errors
from Utils.utils import get_logger
import datetime
from dbconn import Conn


logger = get_logger("blog")


class Article():
    def __init__(self, address, article):
        # tx is { address, article }
        try:
            conn = Conn()
            self.__dict__ |= conn.get_blog(address, article)
            self.date = datetime.datetime.fromtimestamp(float(self.timestamp)).isoformat(timespec="minutes")
            self.link = f"{address}/{article}"
            self.reply = [Message(rep).html() for rep in conn.get_replies(self.txid)]
            try:
                self.profile = Profile(self.address)
            except:
                self.profile = Profile(self.address)
            translations = {"title": "article_title", "text": "article", "support": "support_address", "version": "article_version"}
            for key in translations:
                self.__dict__[key] = self.__dict__[translations[key]]

            logger.info(f"{self.profile.html()}")
        except Exception as e:
            logger.info(f"Exception {type(e)}: {str(e)} in article")
            raise squawker_errors.NotArticle(f"No profile in ipfs hash {tx['article']} got exception {type(e)} {e} from {self.__dict__}")

    def __str__(self):
        try:
            return f"""Name: {self.profile.name}
            {self.text}"""
        except:
            return str(self.__dict__)

    def xml(self):
        return f"""
        <article>
            {self.profile.basic_xml()}
            <block_height>
                {self.tx["block"]}
            </block_height>
            <text>
                {self.text}
            </text>
        </article>
        """

    def html(self):
        try:
            return_dict = {"profile": Profile(self.address).html()}
            for key in ["title", "text", "link", "date", "support", "version", "reply", "txid"]:
                return_dict[key] = self.__dict__[key]
            return return_dict
        except Exception as e:
            logger.info(f"Error producing short html for {self} {str(e)}")
            raise squawker_errors.LoggedBaseException(f"Error producing short html for {self} {str(e)}")

    def short_html(self):
        try:
            return_dict = {"profile": Profile(self.address).html()}
            for key in ["title", "text", "link", "date", "support", "version", "reply", "txid"]:
                if key == "text":
                    return_dict["text"] = " ".join(self.__dict__["text"].split(" ")[0:200])
                    logger.info(f"{return_dict['text']} is the blog text")
                else:
                    return_dict[key] = self.__dict__[key]
            return return_dict
        except Exception as e:
            logger.info(f"Error producing html for {self.__dict__} {type(e)} {str(e)}")
            raise squawker_errors.LoggedBaseException(f"Error producinghtml for {self} {str(e)}")

