from django.db import models


class Stock(models.Model):
    ticker = models.CharField(max_length=5, db_index=True, db_tablespace="indexes")
    name = models.TextField(max_length=100)
    date = models.DateField(db_index=True, db_tablespace="indexes")
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.IntegerField()
    adj_close = models.FloatField()

    class Meta:
        db_tablespace = "tables"

    def __str__(self):              # __unicode__ on Python 2
        return (
            self.ticker,
            self.name,
            self.date,
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
            self.adj_close,
        )
