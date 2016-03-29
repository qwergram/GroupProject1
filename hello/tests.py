from django.test import TestCase
from .stocktwits import get_stock_comments, format_into_table

# Create your tests here.

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
    'reshares': {'reshared_count': 0, 'user_ids': []}}


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
        expected = {
            "social_id": "51852548",
            "source": "stocktwits",
            "focus": "MSFT",
            "popularity": 0,
            "author": "Benzinga",
            "author_image": "https://s3.amazonaws.com/st-avatars/production/7108/thumb-1301323720.png",
            "created_time": '2016-03-28T21:51:06Z',
            "content": 'What This &#39;Esteemed&#39; Venture Capitalist Learned From Mark Zuckerberg $FB $MSFT $YHOO http://stkw.it/d2Ub',
            "symbols": ['MSFT', 'YHOO', 'FB'],
            "urls": 'http://www.benzinga.com/general/entrepreneurship/16/03/7765501/what-this-esteemed-venture-capitalist-learned-from-mark-zucke',
            "url": 'http://stocktwits.com/Benzinga/message/51852548'
        }
        self.assertNotEqual(formatted, expected)
