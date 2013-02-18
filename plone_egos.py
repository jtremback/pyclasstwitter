import requests
from jinja2 import Environment, FileSystemLoader
import os
import shutil


def send_hashtag_report(hashtag, length):
    if os.path.exists('www'):
        delete_files()
    tweets = get_tweets(hashtag)
    write_webpage(tweets, length)
    print "Booyah!"


def get_tweets(hashtag):
    print "Retrieving tweets..."
    tweet_list = []
    search_url = "http://search.twitter.com/search.json?q=%23{0}&include_entities=true".format(hashtag)
    next_page = True
    # Twitter api only serves 15 tweets per request. If json object has 'next_page' value keep
    # loading pages, otherwise stop
    while next_page:
        fp = requests.get(search_url)
        tweets = fp.json()
        for tweet in tweets['results']:
            if tweet['text'][:2] == 'RT':
                continue
            each_tweet = {}
            each_tweet['text'] = tweet['text']
            each_tweet['screen_name'] = tweet['from_user']
            each_tweet['real_name'] = tweet['from_user_name']
            each_tweet['profile_image'] = tweet['profile_image_url']
            each_tweet['id'] = tweet['id']
            each_tweet['created_at'] = tweet['created_at'][5:12] + '--' + tweet['created_at'][16:25]
            each_tweet['media'] = False
            if 'media' in tweet['entities']:
                each_tweet['media'] = tweet['entities']['media'][0]['media_url']
            tweet_list.append(each_tweet)
        if 'next_page' in tweets:
            search_url = "http://search.twitter.com/search.json{0}".format(tweets['next_page'])
        else:
            next_page = False
    return tweet_list


def chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def write_webpage(tweets, length):
    print "Preparing web page..."
    env = Environment(loader=FileSystemLoader('templates'))
    html_template = env.get_template('simple-basic.html')
    if not os.path.exists('www'):
        os.makedirs('www')
    i = 1
    sliced_tweets = chunks(tweets, length)
    for chunk in sliced_tweets:
        page_data = {'prev_page': False, 'next_page': False}
        page_data['current_page'] = i
        if len(sliced_tweets) != i:
            page_data['next_page'] = True
        if i != 1:
            page_data['prev_page'] = True
        page_data['next_page_num'] = i + 1
        page_data['prev_page_num'] = i - 1
        webpage = html_template.render(tweets=chunk, page_data=page_data).encode('utf-8')
        f = open('www/snuf_%s.html' % i, 'w')
        f.write(webpage)
        i += 1


def delete_files():
    print "Cleaing up directory..."
    dir_path = os.path.abspath(os.path.dirname(__file__))
    shutil.rmtree(dir_path + "/www")

if __name__ == '__main__':
    send_hashtag_report("emeraldsprint", 10)
