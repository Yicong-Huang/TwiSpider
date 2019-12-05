import logging
import os

from paths import KEYWORDS_PATH, CACHE_DIR

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(threadName)s:(%(name)s) [%(funcName)s()]   %(message)s')
logger = logging.getLogger(__name__)

from twi_spider import TwiSpider

if __name__ == '__main__':        
    logger.setLevel(logging.DEBUG)
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    with open(KEYWORDS_PATH) as file:
        keywords = [line.rstrip() for line in file]

    TwiSpider(keywords).run()
