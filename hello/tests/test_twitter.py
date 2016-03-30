from django.test import TestCase
from hello.twitter_api import TwitterCli, get_twitter_comments, json_into_table, save_tweets
from hello.models import Message
import datetime
try:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, Request, HTTPError

true = True
false = False
null = None


EXPECTED_TWITTER = {
    "popularity": 40,
    "author_image": "http://pbs.twimg.com/profile_images/546024114272468993/W9gT7hZo_normal.png",
    "source": "twitter",
    "hashtags": [
        "MSFT",
        "Azure",
        "Iaas",
    ],
    "urls": [],
    "focus": "MSFT",
    "author": "Azure",
    "symbols": [],
    "social_id": 17000457,
    "created_time": "2016-03-29T17:56:35Z",
    "content": "#MSFT #Azure is the top choice for companies adopting cloud #IaaS. Read via @siliconangle:https://t.co/unbJ9KkFT2 https://t.co/kDMnH8x6Pc"
}


class TwitterCase(TestCase):
    """Test Twitter API."""

    def test_dne_ticker(self):
        """Test access without auth."""
        wrong = get_twitter_comments("opwuirehe")
        self.assertEqual(wrong, [])

    def test_no_access(self):
        """Test acess without proper auth."""
        with self.assertRaises(HTTPError):
            client = TwitterCli("merp", "1333322")
            client.request()
