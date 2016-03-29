from django.db import models

# Create your models here.


class Company(models.Model):
    ticker = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50, unique=True)
    exchange = models.CharField(max_length=5)
    category = models.CharField(max_length=100)


class Message(models.Model):
    """
    SOURCE
    ======
        The social media site that returned this social data
    FOCUS
    =====
        The stock ticker that was searched for to return this tweet/comment
    POPULARITY
    ==========
        Cumulative likes + retweets/shares + other positive actions by other
        users
    AUTHOR
    ======
        The username/handle of the user who posted this piece of data
    AUTHOR_IMAGE
    ============
        The profile picture of author
    SOCIAL_ID
    =========
        The id of the message on the twitter/stocktwit servers
    CREATED_TIME
    ============
        The time that the message was created
    CONTENT
    =======
        The text of the content/tweet
    SYMBOLS
    =======
        Other symbols mentioned in the text
        Wrapped in a python list fashion
    URLS
    ====
        Other urls mentioned in the text
        includes images/charts/etc.
        wrapped in a python list fashion
    URL
    ===
        Link back to original tweet/comment
    """
    class Meta:
        unique_together = ('source', 'social_id',)

    def __str__(self):
        return "{}[${}]: {}".format(self.source, self.focus, self.content)

    social_id = models.CharField(max_length=32)
    source = models.CharField(max_length=20, choices=(
        ("twitter", "twitter"),
        ("stocktwits", "stocktwits"),
        ("reddit", "reddit"),
    ))
    focus = models.CharField(max_length=5)
    popularity = models.IntegerField()
    author = models.CharField(max_length=16)
    author_image = models.URLField(max_length=16)
    created_time = models.DateTimeField()
    content = models.CharField(max_length=120)
    symbols = models.CharField(max_length=255)
    urls = models.CharField(max_length=255)
    url = models.URLField()


class Stock(models.Model):
    company = models.ForeignKey(Company)
    date = models.DateField(db_index=True, db_tablespace="indexes")
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    # price = models.FloatField()
    # change_in_percent = models.FloatField()
    # change_in_dollars = models.FloatField()
    volume = models.IntegerField()
    adj_close = models.FloatField()

    class Meta:
        db_tablespace = "tables"

    def __str__(self):              # __unicode__ on Python 2
        return (
            self.company.ticker,
            self.company.name,
            self.date,
            self.open,
            self.high,
            self.low,
            # self.price,
            # self.change_in_percent,
            # self.change_in_dollars,
            self.close,
            self.volume,
            self.adj_close,
        )
