from serverside import *
from web_profile import Profile
import json
import squawker_errors
from utils import get_logger
import requests
import datetime

logger = get_logger("blog")


class Article():
    def __init__(self, tx):
        # tx is { address, article, block }
        logger.info(f"starting article {tx}")
        self.tx = tx
        try:
            tx["article"] = tx["message"]
        except:
            pass
        logger.info(f"creating article from {tx}")
        try:
            if isinstance(self.tx["address"], list):
                self.sender = self.tx["address"][0]
            else:
                self.sender = self.tx["address"]
            logger.info(f"{self.sender} sent the article")
            self.raw_article = self.get_raw_article()
            logger.info(f"Article Raw Article is {self.raw_article}")
            self.text = self.raw_article["article"]
            logger.info(f"{self.text} is the article")
            self.title = self.raw_article["article_title"]
            logger.info(f"{self.title} is the article title")
            self.support = self.raw_article["support_address"]
            self.version = self.raw_article["article_version"]
            self.date = datetime.datetime.fromtimestamp(float(self.raw_article["timestamp"])).isoformat(timespec="minutes")
            self.link = self.raw_article["link"]
            try:
                self.profile = Profile(self.sender)
            except:
                self.profile = Profile(self.sender)
            logger.info(f"{self.profile.html()}")
        except Exception as e:
            logger.info(f"Exception {type(e)}: {str(e)} in article")
            raise squawker_errors.NotArticle(f"No profile in ipfs hash {tx['article']} got exception {type(e)} {e} from {self.__dict__}")

    def get_raw_article(self):
        try:
            ipfs_hash = self.tx["article"]
            tx = self.tx
            logger.info(f"get raw_article start {tx} - {ipfs_hash}")
            raw_article = json.loads(ipfs.cat(ipfs_hash))
            if "contents" in raw_article and ("sender" in raw_article or "address" in raw_article) and "metadata_signature" in raw_article:
                params = {'ipfs_hash': ipfs_hash}
                url = 'http://127.0.0.1:8083/api/verify_proxied'
                r = requests.post(url, params=params)
                logger.info(f"{r.text}, {r.status_code}")
                if "True" in r.text:
                    logger.info(f"returned True")
                    first_json = json.loads(ipfs.cat(ipfs_hash))
                    logger.info(f"{first_json} is the first json")
                    logger.info(f"{first_json['contents']} is the first json contents with type {type(first_json['contents'])}")
                    if isinstance(first_json['contents'], str):
                        first_json['contents'] = first_json['contents'].replace("\n", r"\n")
                    raw_article = json.loads(first_json["contents"])
                    logger.info(f"returning {type(raw_article)} {raw_article} from proxied article")
                    try:
                        self.sender = raw_article["sender"]
                    except KeyError:
                        self.sender = raw_article["address"]
                    except Exception as e:
                        logger.info(f"failed setting up profile sender with {type(e)} {str(e)}")
                    try:
                        logger.info(f"{[key for key in tx]} are the keys")
                        raw_article["link"] = f"{self.sender}/{tx['article']}/{tx['block']}"
                    except Exception as e:
                        logger.info(f"Error {type(e)} - {str(e)} from trying to set link")
                    logger.info(f"returning {raw_article}")
                    return raw_article
                else:
                    raise squawker_errors.NotArticle(f"No profile in ipfs hash {tx['article']}")
            else:
                raise squawker_errors.NotArticle(f"No profile in ipfs hash {tx['article']}")
        except squawker_errors.NotArticle as e:
            raise squawker_errors.NotArticle(str(e))
        except Exception as e:
            # print(type(e), e)
            pass

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
            return_dict = {"profile": Profile(self.sender).html()}
            for key in ["title", "text", "link", "date", "support", "version"]:
                return_dict[key] = self.__dict__[key]
            return return_dict
        except Exception as e:
            logger.info(f"Error producing short html for {self} {str(e)}")
            raise squawker_errors.LoggedBaseException(f"Error producing short html for {self} {str(e)}")

    def short_html(self):
        try:
            return_dict = {"profile": Profile(self.sender).html()}
            for key in ["title", "text", "link", "date", "support", "version"]:
                if key == "text":
                    return_dict["text"] = " ".join([self.__dict__["text"].split(" ")[0, 200]])
                    logger.info(f"{return_dict['text']} is the blog text")
                else:
                    return_dict[key] = self.__dict__[key]
            return return_dict
        except Exception as e:
            logger.info(f"Error producing html for {self.__dict__} {type(e)} {str(e)}")
            raise squawker_errors.LoggedBaseException(f"Error producinghtml for {self} {str(e)}")

