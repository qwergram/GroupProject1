from django.test import TestCase
from .stocktwits import get_stock_comments, format_into_table, save_message
from .reddit import (
    get_companies,
    ticker_to_name,
    scrape_reddit,
    save_reddit_articles
)
from .models import Message
import requests

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
    "urls": ['http://www.benzinga.com/general/entrepreneurship/16/03/7765501/what-this-esteemed-venture-capitalist-learned-from-mark-zucke'],
    "url": 'http://stocktwits.com/Benzinga/message/51852548'
}


class RedditScraper(TestCase):

    def test_json_loads(self):
        companies = get_companies()
        expected = {
            "Ticker": "MSFT",
            "Name": "Microsoft Corporation",
            "Exchange": "NMS",
            "Country": "USA",
            "Category Name": "Business Software & Services",
            "Category Number": 826,
            "": 0
        }
        self.assertEqual(companies['MSFT'], expected)

    def test_ticker_to_name_works(self):
        companies = get_companies()
        expected = "Microsoft Corporation"
        self.assertEqual(ticker_to_name(companies, "MSFT"), expected)

    def test_ticker_to_name_bad_company_data(self):
        with self.assertRaises(ValueError):
            ticker_to_name("waffles", "MSFT")

    def test_ticker_to_name_bad_ticker(self):
        companies = get_companies()
        with self.assertRaises(ValueError):
            ticker_to_name(companies, "ayyooo")

    def test_reddit_scraper(self):
        links = scrape_reddit("MSFT", "Microsoft Corporation")
        expected = 'https://www.reddit.com/r/linux/comments/mgtht/given_the_recent_protests_shouldnt_we_point_out/'
        self.assertIn(expected, str(links))

    def test_reddit_save(self):
        links = scrape_reddit("AAPL", ticker_to_name(get_companies(), "SUNE"))
        expected = {
            'url': 'http://www.reddit.com/r/investing/comments/40wx7b/sunedison_inc_to_distribute_tesla_motors_inc/?ref=search_posts',
            'urls': ['https://www.reddit.com/r/investing/comments/40wx7b/sunedison_inc_to_distribute_tesla_motors_inc/'],
            'social_id': '40wx7b',
            'created_time': 1452764067.0,
            'content': 'Sunedison Inc To Distribute Tesla Motors Inc Powerwall',
            'author': 'MartEden',
            'popularity': 27,
            'source': 'reddit',
            'author_image': 'https://www.redditstatic.com/icon-touch.png',
            'focus': 'AAPL',
            'symbols': ['AAPL']
        }
        save_reddit_articles(links)
        dbobj = Message.objects.get(social_id=expected['social_id'])
        self.assertEqual(dbobj.url, expected['url'])
        self.assertEqual(dbobj.urls, expected['urls'])
        self.assertEqual(dbobj.content, expected['content'])
        self.assertEqual(dbobj.author, expected['author'])
        self.assertEqual(dbobj.popularity, expected['popularity'])
        self.assertEqual(dbobj.focus, 'AAPL')


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
