import logging
import logging.handlers


def init():
    global logger
    # logger 인스턴스를 생성 및 로그 레벨 설정
    logger = logging.getLogger("crumbs")
    logger.setLevel(logging.DEBUG)

    # formmater 생성
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s > %(message)s')

    # file_handler와 stream_handler를 생성

    # file max size를 10MB로 설정
    file_max_bytes = 10 * 1024 * 1024
    file_handler = logging.handlers.RotatingFileHandler(filename='./data/hdmeal.log', maxBytes=file_max_bytes,
                                                        backupCount=10, encoding='UTF-8')
    stream_handler = logging.StreamHandler()

    # handler에 fommater 세팅
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Handler를 logging에 추가
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def debug(string):
    logger.debug(string)


def info(string):
    logger.info(string)


def warn(string):
    logger.warning(string)


def err(string):
    logger.error(string)


def critical(string):
    logger.critical(string)
