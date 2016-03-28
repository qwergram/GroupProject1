from client import Client
import os

key = os.environ.get('CONSUMER_KEY')
secret = os.environ.get('CONSUMER_SECRET')

client = Client(key, secret)
apple = client.request('https://api.twitter.com/1.1/search/tweets.json\
                        ?q=%23aaple&result_type=recent')
print(apple)
