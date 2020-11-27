import logging


def get_logger(name, filename, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    fh = logging.FileHandler(filename)
    ch = logging.StreamHandler()

    fh.setLevel(level)
    ch.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


CIS = False
LOG = get_logger("analytics", "logs/analytics.log")


es_index_url = "http://127.0.0.1:9200/bible_index"
es_index_url_noedge = "http://127.0.0.1:9200/bible_index_noedge"
