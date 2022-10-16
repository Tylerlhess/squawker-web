from ServerEssentials.serverside import *
from Utils.utils import get_logger
from dbconn import Conn


logger = get_logger('squawker_profile')


class Profile:
    def __init__(self, address):
        try:
            conn = Conn()
            self.__dict__ |= conn.get_profile(address)
            self.picture = None
        except TypeError as e:
            logger.info(f"Logging error {e}")
            self.address = address
            self.picture = ipfs.cat("QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg")
            self.profile_picture = "QmcbpiAD84yYUs48ftHZS2smRMqsUpPcYamoqh7pHjBzfg"


    def basic_xml(self):
        return f"""
        <profile>
            <profile_image>
                {self.profile_picture}
            </profile_image>
            <profile_name>
                {self.name}
            </profile_name>
        </profile>"""

    def basic_html(self):
        return f"""
        <div class="profile">
            <div class="profile_img">
                <img source="squawker.badguyty.com/ipfs/{self.profile_picture}">

            </div>
            <div class="profile_content">
                <div class="profile_name">
                    {self.name}
                </div>
            </div>
        </div>"""

    def html(self):
        html_dict = dict()
        for atb in self.__dict__:
            if atb == "picture":
                html_dict["picture"] = self.profile_picture
            elif atb == "name":
                html_dict["name"] = self.name
            elif atb == "address":
                html_dict["address"] = self.address
            else:
                if "others" not in html_dict:
                    html_dict["others"] = dict()
                if not callable(atb):
                    html_dict["others"][atb] = self.__dict__[atb]
        return html_dict

    def report(self):
        return f"profile {self.__str__()}"

    def json(self):
        return {'ipfs_hash': self.ipfs_hash, 'address': self.address, 'profile_picture': self.profile_picture,
                'picture': str(self.picture)}

