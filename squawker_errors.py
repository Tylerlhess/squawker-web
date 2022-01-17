import logging

logger = logging.getLogger('squawker_errors')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='squawker_errors.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
handler2 = logging.FileHandler(filename='squawker.log', encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler2)


class LoggedBaseException(BaseException):
    def __init__(self, message=""):
        self.message = message
        logger.info(f"logging error {self.__name__} {self.message} ")
        super().__init__(self.message)


class InvalidProfileJSON(LoggedBaseException):
    pass


class NotMessage(LoggedBaseException):
    pass


class NotRegistered(LoggedBaseException):
    pass


class NoProfile(LoggedBaseException):
    pass


class BadCredentials(LoggedBaseException):
    pass


class AlreadyRegistered(LoggedBaseException):
    pass


class NotListing(LoggedBaseException):
    pass


class TransactionError(LoggedBaseException):
    pass