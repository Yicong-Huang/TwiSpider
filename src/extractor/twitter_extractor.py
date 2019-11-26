import datetime
import json
import logging
from datetime import datetime
from typing import List, Iterable

from twitter import Status

from crawlers.twitter_id_mode_crawler import TweetIDModeCrawler
from extractor.extractorbase import ExtractorBase

logger = logging.getLogger(__name__)


class TweetExtractor(ExtractorBase):
    def __init__(self):
        super().__init__()
        self.data: list = []

    def extract(self, tweets: Iterable[Status]) -> List:
        """extracts useful information after being provided with original tweet data (similar to a filter)"""
        collected_ids = set()
        self.data.clear()
        for tweet in tweets:
            id = tweet.id
            if id not in collected_ids:
                collected_ids.add(id)
                # extracts (filters) the useful information
                user = tweet.user

                [[top_left, _, bottom_right, _]] = tweet.place['bounding_box']['coordinates'] if tweet.place else [
                    [None] * 4]

                self.data.append(
                    {'id': id, 'date_time': datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y'),
                     'full_text': tweet.full_text, 'hash_tags': [tag.text for tag in tweet.hashtags],
                     'top_left': top_left,
                     'bottom_right': bottom_right,
                     'original_tweet_retweet_count': tweet.retweet_count,
                     'profile_pic': user.profile_image_url,
                     'screen_name': user.screen_name,
                     'user_name': user.name,
                     'created_date_time': datetime.strptime(tweet.user.created_at, '%a %b %d %H:%M:%S %z %Y'),
                     'followers_count': user.followers_count,
                     'favourites_count': user.favourites_count, 'friends_count': user.friends_count, 'user_id': user.id,
                     'user_location': user.location if user.geo_enabled else 'None',
                     'statuses_count': user.statuses_count})

        return self.data
        # stores self.data and returns a reference of it

    def export(self, file_type: str, file_name: str) -> None:
        """exports data with specified file type"""
        # for example, json
        replace_list = list(self.data)
        # make replace_list equal to self.data and change it
        if file_type == 'json':
            for each_extractor_line in replace_list:
                each_extractor_line['date_time'] = str(each_extractor_line['date_time'])
                # json does not accept datetime values, does change it into string
            json.dump(replace_list, open(file_name, 'w'))


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    tweet_id_mode_crawler = TweetIDModeCrawler()
    tweet_extractor = TweetExtractor()

    raw_ids = [1198260660263624704, 1198260018602237952, 1198249993070624770, 1198238472206729216,
               1198238463063187456, 1198254653827366917, 1198257144744890374, 1198236032803758080,
               1198227110843863043, 1198218486511808513, 1198215395024527360, 1198144558049189889,
               1198094686507982849, 1198089147803557890, 1198081137106657282, 1198059467323121666,
               1198173800434749440, 1198195017795407872, 1198115743180689408, 1198073343729111040,
               1198047793845280768, 1198144719030759424, 1198157405705650176, 1198039714529447937,
               1198152680960675840]

    status = tweet_id_mode_crawler.crawl(raw_ids)
    print(tweet_extractor.extract(status))
