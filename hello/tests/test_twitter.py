from django.test import TestCase
from hello.twitter_api import TwitterCli, get_twitter_comments, json_into_table
import io
import json
from urllib.error import HTTPError

with io.open("hello/tests/example_twit.json") as samplejson:
    SAMPLE_JSON = json.loads(samplejson.read())

EXPECTED_TWITTER = {
    "symbols": [],
    "author": "Duane Newman",
    "hashtags": [
        "MSFT",
        "Build2016",
        "mountaindew",
        "bldwin",
        "BeverageFail",
        "HadToDrinkPepsi"
    ],
    "source": "twitter",
    "focus": "MSFT",
    "author_image": "http://pbs.twimg.com/profile_images/558825363619344386/gUN09sSf_normal.jpeg",
    "urls": [],
    "created_time": "2009-01-29T21:01:24Z",
    "popularity": 0,
    "content": "Hey #MSFT, I thought #Build2016 was a developer conference. Where's the #mountaindew? #bldwin #BeverageFail #HadToDrinkPepsi",
    "social_id": 19734130
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
            resp = client.request("https://api.twitter.com/1.1/search/tweets.json?q=%23MSFT")
            return resp

    def test_json_to_table(self):
        """Test the corrected format from json to db."""
        jsonified = json_into_table(SAMPLE_JSON, "MSFT")
        self.assertEqual(EXPECTED_TWITTER, jsonified)

    def test_invalid_json(self):
        """Test passing in message with invalid ticker."""
        with self.assertRaises(ValueError):
            so_true = False
            json_into_table(SAMPLE_JSON, so_true)
