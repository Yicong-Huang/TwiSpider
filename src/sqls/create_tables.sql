create table if not exists tweets
(
    id                           bigint not null
        constraint tweets_pk
            primary key,
    create_at                    timestamp,
    text                         text,
    original_tweet_retweet_count integer,
    location                     text,
    hash_tags                    text,
    profile_pic                  text,
    screen_name                  text,
    user_name                    text,
    created_date_time            timestamp,
    followers_count              integer,
    favourites_count             integer,
    friends_count                integer,
    user_id                      bigint,
    user_location                text,
    statuses_count               integer
);

create table if not exists retweet_of
(
    original_tweet_id bigint not null
        constraint retweet_of_tweets_id_fk
            references tweets,
    retweet_tweet_id  bigint not null
        constraint retweet_of_tweets_id_fk_2
            references tweets,
    constraint retweet_of_pk
        primary key (original_tweet_id, retweet_tweet_id)
);
