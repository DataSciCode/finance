from django.db import models

# Create your models here.

class Snapshot(models.Model):
    snapshot = models.DateTimeField()

class Stock(models.Model):
    snapshot = models.ForeignKey(Snapshot)

    Ticker = models.CharField(max_length=10)
    Company = models.CharField(max_length=100)
    MarketCap = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    PE = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    PS = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    PB = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    PFreeCashFlow = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    DividendYield = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    PerformanceHalfYear = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    Price = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    BB = models.DecimalField(null=True, max_digits=20, decimal_places=2)
    EVEBITDA = models.DecimalField(null=True, max_digits=20, decimal_places=2)

    BBY = models.DecimalField(null=True, max_digits=20, decimal_places=2)
    SHY = models.DecimalField(null=True, max_digits=20, decimal_places=2)

    PERank = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    PSRank = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    PBRank = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    PFCRank = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    SHYRank = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    EVEBITDARank = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    Rank = models.DecimalField(null=True, max_digits=5, decimal_places=2)
    OVRRank = models.DecimalField(null=True, max_digits=5, decimal_places=2)
