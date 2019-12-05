import logging

from paths import KEYWORDS_PATH

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(threadName)s:(%(name)s) [%(funcName)s()]   %(message)s')
logger = logging.getLogger(__name__)

from twi_spider import TwiSpider

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    with open(KEYWORDS_PATH) as file:
        keywords = [line.rstrip() for line in file]

    TwiSpider(keywords).run()
