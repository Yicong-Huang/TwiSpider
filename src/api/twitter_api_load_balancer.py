import twitter

from paths import TWITTER_API_CONFIG_PATH
from utilities.ini_parser import parse


class TwitterAPILoadBalancer:
    def __init__(self):
        self.apis = [twitter.Api(**config, sleep_on_rate_limit=True) for config in
                     parse(TWITTER_API_CONFIG_PATH).values()]
        self.iter_index = -1

    def get(self):
        self.iter_index += 1
        if self.iter_index == len(self):
            self.iter_index = 0
        return self.apis[self.iter_index]

    def __len__(self):
        return self.apis.__len__()


if __name__ == '__main__':
    twitter_api_load_balancer = TwitterAPILoadBalancer()
    for i in range(19):
        twitter_api_load_balancer.get()
