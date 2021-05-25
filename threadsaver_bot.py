import tweepy
import logging
import os
import time
import credentials


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()



def create_api():
    consumer_key = 'CONSUMER_KEY'
    consumer_secret = "CONSUMER_SECRET"
    access_token = "ACCESS_TOKEN"
    access_token_secret = "ACCESS_TOKEN_SECRET"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
        print('verified')
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api


def direct_message(api,user_name, id, url):
    message_text = f"Your saved thread {url}"
    print(user_name, url)
    user = api.get_user(id)
    user_id = user.id_str
    api.send_direct_message(user_id, message_text)
    print(f"Successfully sent to {user.name}")


def getRootTweet(api, tweet):
    if tweet is None:
        print("fatal error: Tweet null")
        logger.info(f"{tweet.user.name},{tweet.id}")
        return tweet.user.screen_name,tweet.id
    if tweet.in_reply_to_status_id is None:
        print("Got root!")
        logger.info(f"{tweet.user.name},{tweet.id}")
        return tweet.user.screen_name,tweet.id
    parent = api.get_status(tweet.in_reply_to_status_id, tweet_mode="extended")
    return getRootTweet(api, parent)


def retrieve_userthread(api):
    keywords = ['save','shot']
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline,
                               since_id=since_id).items():
        logger.info(tweet.user.screen_name)
        logger.info(f"Since ID:{since_id}")
        new_since_id = max(tweet.id, new_since_id)
        logger.info(f"new Since ID:{new_since_id}")
        # if tweet.in_reply_to_status_id is not None:
        #     continue
        if any(keyword in tweet.text.lower() for keyword in keywords):
            tag_user = tweet.user.name
            tag_id = tweet.user.id
            logger.info(f"Finding parent of {tag_user}")

            parent_username, parent_id = getRootTweet(api, tweet)

            thread_url = f"https://twitter.com/{parent_username}/status/{parent_id}"

            direct_message(api,tag_user, tag_id, thread_url)

    return new_since_id


api = create_api()
since_id = 'id'
while True:
    since_id = retrieve_userthread(api)
    print("break")
    logger.info("Waiting...")
    time.sleep(10)