import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(threadName)s:(%(name)s) [%(funcName)s()]   %(message)s')
logger = logging.getLogger(__name__)

from twi_spider import TwiSpider

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    with open('keywords.txt') as file:
        keywords = [line.rstrip() for line in file]

    TwiSpider(keywords).run()
