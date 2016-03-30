# coding=utf-8
from django.test import TestCase, Client, TransactionTestCase
from hello.stocktwits import get_stock_comments, format_into_table, save_message
# from .twitter_api import Client, ClientException, get_twitter_comments, json_into_table
from hello.models import Message
# import os
import requests
import datetime
import os

# Create your tests here.
# false = False
# true = True

EXAMPLE_RESPONSE = {
    'body': 'What This &#39;Esteemed&#39; Venture Capitalist Learned From Mark Zuckerberg $FB $MSFT $YHOO http://stkw.it/d2Ub',
    'symbols': [
        {'symbol': 'MSFT', 'id': 2735, 'title': 'Microsoft Corporation'},
        {'symbol': 'YHOO', 'id': 4177, 'title': 'Yahoo! Inc.'},
        {'symbol': 'FB', 'id': 7871, 'title': 'Facebook'}
    ], 'user': {
        'identity': 'Official',
        'classification': ['suggested', 'official'],
        'avatar_url_ssl': 'https://s3.amazonaws.com/st-avatars/production/7108/thumb-1301323720.png',
        'id': 7108,
        'name': 'Benzinga',
        'avatar_url': 'http://avatars.stocktwits.com/production/7108/thumb-1301323720.png',
        'official': True,
        'join_date': '2009-12-04',
        'username': 'Benzinga'
    },
    'id': 51852548,
    'links': [
        {
            'source': {
                'website': 'http://www.benzinga.com',
                'name': 'Benzinga'
            },
            'image': 'http://cdn3.benzinga.com/files/imagecache/story_image_685x375C/images/story/2012/2321206299_5038c90c4e_o.jpg',
            'video_url': None,
            'url': 'http://www.benzinga.com/general/entrepreneurship/16/03/7765501/what-this-esteemed-venture-capitalist-learned-from-mark-zucke',
            'description': 'Chamath Palihapitiya runs one of the best-respected venture capital firms in Silicon Valley, Social Capital, which has backed several tech companies with valuations in the billions, including Slack, Box and SurveyMonkey. Vanity Fair recently interviewed Palihapitiya. The former Facebook Inc (NASDAQ: FB) employee went into multiple issues, and this article will focus on what the investor learned from working side-by-side with Mark Zuckerberg.',
            'shortened_url': 'http://stkw.it/d2Ub',
            'title': "Facebook, Inc. (NASDAQ:FB), Microsoft Corporation (NASDAQ:MSFT) - What This 'Esteemed' Venture Capitalist Learned From Mark Zuckerberg",
            'created_at': '2016-03-28T21:51:09Z', 'shortened_expanded_url': 'benzinga.com/general/entrep...'
        }
    ], 'source': {
        'title': 'StockTwits',
        'id': 1,
        'url': 'http://stocktwits.com'
    },
    'created_at': '2016-03-28T21:51:06Z',
    'reshares': {'reshared_count': 0, 'user_ids': []}
}

EXPECTED = {
    "social_id": "51852548",
    "source": "stocktwits",
    "focus": "MSFT",
    "popularity": 0,
    "author": "Benzinga",
    "author_image": "https://s3.amazonaws.com/st-avatars/production/7108/thumb-1301323720.png",
    "created_time": '2016-03-28T21:51:06Z',
    "content": 'What This \'Esteemed\' Venture Capitalist Learned From Mark Zuckerberg $FB $MSFT $YHOO http://stkw.it/d2Ub',
    "symbols": ['MSFT', 'YHOO', 'FB'],
    "hashtags": [],
    "urls": ['http://www.benzinga.com/general/entrepreneurship/16/03/7765501/what-this-esteemed-venture-capitalist-learned-from-mark-zucke'],
    "url": 'http://stocktwits.com/Benzinga/message/51852548'
}

# EXPECTED_TWITTER = {
#     "popularity": 1,
#     "author_image": "http://pbs.twimg.com/profile_images/696574346597416960/Pcp9o6nP_normal.jpg",
#     "hashtags": [
#       "MSFT",
#       "Machine",
#       "Learning",
#       "Technology",
#       "human",
#       "intelligence"
#     ],
#     "urls": [],
#     "focus": "MSFT",
#     "author": "Alexander Felke",
#     "symbols": [],
#     "social_id": 3759215603,
#     "created_time": "Thu Sep 24 10:33:18 +0000 2015",
#     "content": "#MSFT is beefing up #Machine #Learning: #Technology advances #human #intelligence. I say mid term."
# }


class StockTwitsCase(TestCase):

    def test_error_is_raised(self):
        with self.assertRaises(ValueError):
            get_stock_comments("not a real company")

    def test_response_length(self):
        response = get_stock_comments("MSFT")
        self.assertEqual(len(response), 30)

    def test_response_contains_id(self):
        response = get_stock_comments("MSFT")
        for r in response:
            self.assertNotEqual(r.get('id'), None)

    def test_response_contains_body(self):
        response = get_stock_comments("MSFT")
        for r in response:
            self.assertNotEqual(r.get('body'), None)

    def test_json_trimmer(self):
        formatted = format_into_table(EXAMPLE_RESPONSE, "MSFT")
        self.assertEqual(formatted, EXPECTED)

    def test_database_save_return(self):
        self.assertTrue(save_message(EXPECTED))
        self.assertFalse(save_message(EXPECTED))

    def test_database_save_database(self):
        save_message(EXPECTED)
        m = Message.objects.get(social_id="51852548")
        self.assertEqual(m.focus, "MSFT")
        self.assertEqual(m.url, "http://stocktwits.com/Benzinga/message/51852548")

    def test_text_is_correct(self):
        save_message(EXPECTED)
        message = Message.objects.get(social_id="51852548")
        document = requests.get(message.url).text
        self.assertIn(message.content, document)


class MovingStocksCase(TestCase):
    def yahoo_data(self):
        with open(os.path.join("hello", "testdata", "yahoo_data.htmlfragment"), 'r', encoding='utf-8') as f:
            return f.read()

    def test_yahoo_data(self):
        from hello.moving_stocks import _yahoo_top_movers, TopMover
        import hello.moving_stocks
        hello.moving_stocks._yahoo_cached = None  # ensure cache is cleared
        data = self.yahoo_data()
        movers = _yahoo_top_movers(data)
        self.assertEqual(movers, [
            TopMover("SUNE", "SunEdison, Inc.", 0.57, -0.69, -54.76, 147037800),
            TopMover("BAC", "Bank of America Corporation", 13.42, -0.2, -1.47, 101526412),
            TopMover("HOLX", "Hologic Inc.", 34.5, -0.07, -0.2, 52960883),
            TopMover("ESV", "Ensco plc", 10.3, -0.42, -3.92, 51307639),
            TopMover("FCX", "Freeport-McMoRan Inc.", 10.14, 0, 0, 44196028),
            TopMover("CNC", "Centene Corp.", 62.6, 0.21, 0.34, 39208539),
            TopMover("GE", "General Electric Company", 31.48, -0.01, -0.03, 38548937),
            TopMover("CRC", "California Resources Corporation", 1.05, -0.12, -10.26, 35801398),
            TopMover("PFE", "Pfizer Inc.", 30.05, 0.27, 0.91, 34596186),
            TopMover("AAPL", "Apple Inc.", 107.68, 2.49, 2.37, 31176911),
            TopMover("MU", "Micron Technology, Inc.", 10.45, 0.07, 0.67, 30888521),
            TopMover("QQQ", "PowerShares QQQ ETF", 108.83, 1.72, 1.61, 29949401),
            TopMover("FB", "Facebook, Inc.", 116.14, 2.45, 2.15, 29812606),
            TopMover("CHK", "Chesapeake Energy Corporation", 4.04, -0.11, -2.65, 28456020),
            TopMover("PBR", "Petróleo Brasileiro S.A. - Petrobras", 5.83, 0.04, 0.69, 27202507),
            TopMover("VRX", "Valeant Pharmaceuticals International, Inc.", 28.98, 0.12, 0.42, 26872253),
            TopMover("ITUB", "Itaú Unibanco Holding S.A.", 8.73, 0.04, 0.46, 26874125),
            TopMover("F", "Ford Motor Co.", 13.2, 0.11, 0.84, 26062180),
            TopMover("T", "AT&T, Inc.", 39.45, 0.38, 0.97, 25892774),
            TopMover("KO", "The Coca-Cola Company", 46.48, 0.68, 1.48, 25009987),
        ])
        # make sure it is caching
        self.assertTrue(_yahoo_top_movers(data) is movers)


class HistoricalCase(TestCase):
    pass
