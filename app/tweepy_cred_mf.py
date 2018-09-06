import tweepy

####input your credentials here
consumer_key = '1V7huH9UUcNKIlEM1b2SAEPVj'
consumer_secret = 'nNHDnO61A7UEzxC8H1V7YFCgQCvdrdkdtILYbsgnKeUAoGnEkA'
access_token = '1029826578086354960-T2mU4tI9enTE48qiy4v8FBocBv3yCF'
access_token_secret = 'dUjp7YRAlkCaVQqkK90FtZbmgAu2nnP42iJU4SpLEGWdt'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


#Mashape credentials
mashape_key = 'HeNcBWxMcomshdqzurzBDSJd0J0Mp1nXtoUjsnnnxBycdo0ROQ'

twitter_app_auth = {
        'consumer_key' : '1V7huH9UUcNKIlEM1b2SAEPVj',
        'consumer_secret' : 'nNHDnO61A7UEzxC8H1V7YFCgQCvdrdkdtILYbsgnKeUAoGnEkA',
        'access_token' : '1029826578086354960-T2mU4tI9enTE48qiy4v8FBocBv3yCF',
        'access_token_secret' : 'dUjp7YRAlkCaVQqkK90FtZbmgAu2nnP42iJU4SpLEGWdt'
    }
