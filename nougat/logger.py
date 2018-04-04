import logging


def get_logger(log_level=logging.DEBUG):

    # create logger
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.ERROR)

    ch = logging.StreamHandler()

    ch.setLevel(log_level)

    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s %(name)-12s %(levelname)-8s %(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.handlers = [ch]

    return logger
