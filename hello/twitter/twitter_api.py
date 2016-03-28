from client import Client
import os

key = os.environ.get('Qy7ThBysBdMa1zwosebGYoXXD')
secret = os.environ.get('bggZOTTkq4gwoyD2K7VuTqtvAqwdbEgXAFnZgHCvVhAQLEsTqj')

client = Client(key, secret)
apple = client.request('https://api.twitter.com/1.1/search/tweets.json\
                        ?q=%23aaple&result_type=recent')
print(apple)
