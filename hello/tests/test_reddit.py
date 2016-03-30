from django.test import TestCase
import datetime
from hello.models import Message
from hello.reddit import (
    get_companies,
    ticker_to_name,
    scrape_reddit,
    save_reddit_articles
)


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
            'created_time': datetime.datetime.utcfromtimestamp(1452764067.0).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
        self.assertEqual(dbobj.urls, str(expected['urls']))
        self.assertEqual(dbobj.content, expected['content'])
        self.assertEqual(dbobj.author, expected['author'])
        self.assertEqual(dbobj.focus, 'AAPL')
