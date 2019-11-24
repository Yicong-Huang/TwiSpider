import logging

from dumpers.dumperbase import DumperBase
from utilities.connection import Connection

logger = logging.getLogger(__name__)


class TweetRetweetOfDumper(DumperBase):

    def __init__(self):
        super().__init__()

    def insert(self, original_tweet_id, retweet_id) -> None:
        Connection.sql_execute_commit(
            f"INSERT INTO retweet_of values ({original_tweet_id}, {retweet_id}) ON CONFLICT DO NOTHING")


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    tweet_dumper = TweetRetweetOfDumper()

    # id mode tests:
    tweet_dumper.insert(1, 2)
