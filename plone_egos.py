import requests
import urllib
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
    return [l[i:i+n] for i in range(0, len(l), n)]

def write_webpage(tweets, length):
    print "Preparing web page..."
    env = Environment(loader=FileSystemLoader('templates'))
    html_template = env.get_template('simple-basic.html')

    if not os.path.exists('www'):
        os.makedirs('www')
    i = 0

    sliced_tweets = chunks(tweets, length)
    for chunk in sliced_tweets:
        webpage = html_template.render(tweets=chunk).encode('utf-8')
        f = open('www/snunderflow_%s.html'% i, 'w')
        f.write(webpage)
        i += 1

def delete_files():
    print "Cleaing up directory..."
    dir_path = os.path.abspath(os.path.dirname(__file__))
    shutil.rmtree(dir_path + "/www")

if __name__ == '__main__':
    send_hashtag_report("emeraldsprint", 10)

# def get_images(tweet_list):
#     print "Downloading images..."
#     avatars_downloaded = []
#     tweet_images_downloaded = []
#     for tweet in tweet_list:
#         if tweet['screen_name'] not in avatars_downloaded:
#             urllib.urlretrieve(tweet['profile_image'], '{0}_av'.format(tweet['screen_name']))
#             avatars_downloaded.append(tweet['screen_name'])
#         if tweet['media']:
#             urllib.urlretrieve(tweet['media'], '{0}_im'.format(tweet['id']))
#             tweet_images_downloaded.append('{0}_im'.format(tweet['id']))
#     return avatars_downloaded, tweet_images_downloaded

# def prepare_email(tweets):
#     print "Preparing email..."
#     env = Environment(loader=FileSystemLoader('templates'))
#     html_template = env.get_template('simple-basic.html')
#     plain_template = env.get_template('plaintext_email')
#     html_email = html_template.render(tweets=tweets)
#     plain_email = plain_template.render(tweets=tweets)
#     # Converts all css stylings from those in the <head></head> into inline styling
#     # so the email client doesn't rip them out.
#     html_email = premailer.transform(html_email)
#     return html_email, plain_email

# def send_email(addresses, host, port, from_address, subject, html_email,
#                plain_email, avatars, tweet_images):
#     password = raw_input('Password: ')
#     print "Sending email..."
#     msgRoot = MIMEMultipart('related')
#     msgRoot['Subject'] = subject
#     msgRoot['From'] = from_address
#     msgRoot['To'] = ', '.join(addresses)
#     msgRoot.epilogue = ''

#     msgAlternative = MIMEMultipart('alternative')
#     msgRoot.attach(msgAlternative)

#     msgText = MIMEText(plain_email.encode('utf-8'))
#     msgAlternative.attach(msgText)

#     msgText = MIMEText(html_email.encode('utf-8'), 'html')
#     msgAlternative.attach(msgText)

#     for avatar in avatars:
#         with open("{0}_av".format(avatar), 'rb') as fp:
#             msgImage = MIMEImage(fp.read())
#             msgImage.add_header('Content-ID', '<{0}_av>'.format(avatar))
#             msgRoot.attach(msgImage)
#     for tweet_image in tweet_images:
#         with open(tweet_image, 'rb') as fp:
#             msgImage = MIMEImage(fp.read())
#             msgImage.add_header('Content-ID', '<{0}>'.format(tweet_image))
#             msgRoot.attach(msgImage)
#     with open("plone-logo.png", 'rb') as fp:
#         msgImage = MIMEImage(fp.read())
#         msgImage.add_header('Content-ID', '<plone-logo.png>')
#         msgRoot.attach(msgImage)    

#     session = smtplib.SMTP(host, port)
#     session.starttls()
#     session.login(from_address, password)
#     session.sendmail(from_address, addresses, msgRoot.as_string())
#     session.quit()
