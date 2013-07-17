import requests
import csv
from models import Stock, Snapshot
import yql
import pdb
from datetime import datetime
from decimal import Decimal
import time

def csv_to_dicts(scsv):
    import StringIO
    reader = csv.reader(StringIO.StringIO(scsv))
    header = []
    res = []
    for row in reader:
        if header:
            data = {}
            for i,val in enumerate(row):
                data[header[i]] = val
            res.append(data)
        else:
            header = row
    return res

def import_data():
    snapshot = Snapshot()
    snapshot.snapshot = datetime.now()
    snapshot.save()

    print "Importing data from finviz"
    r = requests.get('http://finviz.com/export.ashx?v=152', cookies={"screenerUrl": "screener.ashx?v=152&f=cap_smallover&ft=4", "customTable": "0,1,2,6,7,10,11,13,14,45,65"})
    data = csv_to_dicts(r.text)
    tickers = []
    for row in data:
        try:
            stock = Stock()
            stock.snapshot = snapshot
            if row["Ticker"]:
                stock.Ticker = row["Ticker"]
            print stock.Ticker
            tickers.append(stock.Ticker)
            if "Importing " + row["Company"]:
                stock.Company = row["Company"]
            if row["Market Cap"]:
                stock.MarketCap = row["Market Cap"]
            if row["P/E"]:
                stock.PE = row["P/E"]
            if row["P/S"]:
                stock.PS = row["P/S"]
            if row["P/B"]:
                stock.PB = row["P/B"]
            if row["P/Free Cash Flow"]:
                stock.PFreeCashFlow = row["P/Free Cash Flow"] 
            if row["Dividend Yield"]:
                stock.DividendYield = row["Dividend Yield"][:-1]
            if row["Performance (Half Year)"]:
                stock.PerformanceHalfYear = row["Performance (Half Year)"][:-1]
            if row["Price"]:
                stock.Price = row["Price"]
            stock.save()
        except:
            pdb.set_trace()
            

    import_evebitda(snapshot)

    import_buyback_yield(snapshot)

def import_evebitda(snapshot, startwith=None):
    print "Importing EV/EBITDA"
    if startwith:
        stocks = Stock.objects.filter(snapshot=snapshot, Ticker__gte=startwith)
    else:
        stocks = Stock.objects.filter(snapshot=snapshot)
    tickers = []
    for stock in stocks:
        tickers.append(stock.Ticker)

    y = yql.Public()
    step=100
    for i in range(0,len(tickers),step):
        print "From " + tickers[i] + " to " + tickers[min(i+step,len(tickers))-1]
        nquery = 'select symbol, EnterpriseValueEBITDA.content from yahoo.finance.keystats where symbol in ({0})'.format('"'+('","'.join(tickers[i:i+step-1])+'"'))
        ebitdas = y.execute(nquery, env="http://www.datatables.org/alltables.env")
        if ebitdas.results:
            for row in ebitdas.results["stats"]:
                print row["symbol"]
                if "EnterpriseValueEBITDA" in row and row["EnterpriseValueEBITDA"] and row["EnterpriseValueEBITDA"] != "N/A":
                    stock = Stock.objects.get(snapshot=snapshot, Ticker=row["symbol"])
                    stock.EVEBITDA = row["EnterpriseValueEBITDA"]
                    stock.save()
        else:
            print "No results"

def import_buyback_yield(snapshot, startwith=None):
    print "Importing Buyback Yield"
    if startwith:
        stocks = Stock.objects.filter(snapshot=snapshot, Ticker__gte=startwith)
    else:
        stocks = Stock.objects.filter(snapshot=snapshot)
    for stock in stocks:
        done = False
        while not done:
            try:
                print stock.Ticker
                if not stock.MarketCap: break
                r = requests.get("http://finance.yahoo.com/q/cf?s="+stock.Ticker+"&ql=1")
                html = r.text
                # Repair html
                html = html.replace('<div id="yucs-contextual_shortcuts"data-property="finance"data-languagetag="en-us"data-status="active"data-spaceid=""data-cobrand="standard">', '<div id="yucs-contextual_shortcuts" data-property="finance" data-languagetag="en-us" data-status="active" data-spaceid="" data-cobrand="standard">')
                from BeautifulSoup import BeautifulSoup
                soup = BeautifulSoup(html)
                table = soup.find("table", {"class": "yfnc_tabledata1"})
                if not table: break
                table = table.find("table")
                if not table: break
                sale = 0
                for tr in table.findAll("tr"):
                    title = tr.td.renderContents().strip()
                    if title == "Sale Purchase of Stock":
                        for td in tr.findAll("td")[1:]:
                            val = td.renderContents().strip()
                            val = val.replace("(", "-")
                            val = val.replace(",", "")
                            val = val.replace(")", "")
                            val = val.replace("&nbsp;", "")
                            val = val.replace("\n", "")
                            val = val.replace("\t", "")
                            val = val.replace("\\n", "")
                            val = val.replace(" ", "")
                            if val == "-": continue
                            sale += int(val)*1000
                stock.BB = -sale
                stock.save()
                done = True
                print "done!"
            except Exception as e:
                print e
                print "Trying again in 1 sec"
                time.sleep(1)

#def set_placeholders(snapshot):
    # TODO

def compute_rank(snapshot, step=0):
    if step == 0:
        compute_perank(snapshot)
    if step <=1:
        compute_psrank(snapshot)
    if step <=2:
        compute_pbrank(snapshot)
    if step <=3:
        compute_pfcfrank(snapshot)
    if step <=4:
        compute_bby(snapshot)
    if step <=5:
        compute_shy(snapshot)
    if step <=6:
        compute_shyrank(snapshot)
    if step <=7:
        compute_evebitdarank(snapshot)
    if step <=8:
        compute_stockrank(snapshot)
    if step <=9:
        compute_overallrank(snapshot)

def compute_perank(snapshot):
    print "Computing PE rank"
    i = 0
    PE = None
    stocks = Stock.objects.filter(snapshot=snapshot).order_by("-PE")
    amt = stocks.count()
    for stock in stocks:
        print stock.Ticker
        if stock.PE != PE:
            last_rank = i
        stock.PERank = Decimal(last_rank)/amt*100
        stock.save()
        i +=1

def compute_psrank(snapshot):
    print "Computing PS rank"
    i = 0
    PS = None
    stocks = Stock.objects.filter(snapshot=snapshot).order_by("-PS")
    amt = stocks.count()
    for stock in stocks:
        print stock.Ticker
        if stock.PS != PS:
            last_rank = i
        stock.PSRank = Decimal(last_rank)/amt*100
        stock.save()
        i +=1

def compute_pbrank(snapshot):
    print "Computing PB rank"
    i = 0
    PB = None
    stocks = Stock.objects.filter(snapshot=snapshot).order_by("-PB")
    amt = stocks.count()
    for stock in stocks:
        print stock.Ticker
        if stock.PB != PB:
            last_rank = i
        stock.PBRank = Decimal(last_rank)/amt*100
        stock.save()
        i +=1

def compute_pfcfrank(snapshot):
    print "Computing PFCF rank"
    i = 0
    PFCF = None
    stocks = Stock.objects.filter(snapshot=snapshot,PFreeCashFlow__isnull=False).order_by("-PFreeCashFlow")
    amt = stocks.count()
    for stock in stocks:
        print stock.Ticker
        if stock.PFreeCashFlow != PFCF:
            last_rank = i
        stock.PFCRank = Decimal(last_rank)/amt*100
        stock.save()
        i +=1

def compute_bby(snapshot):
    print "Computing BBY"
    for stock in Stock.objects.filter(snapshot=snapshot, BB__isnull=False, MarketCap__isnull=False):
        print stock.Ticker
        stock.BBY = -Decimal(stock.BB)/(stock.MarketCap*1000000)*100
        stock.save()

def compute_shy(snapshot):
    print "Computing SHY"
    for stock in Stock.objects.filter(snapshot=snapshot):
        print stock.Ticker
        stock.SHY = 0
        if stock.DividendYield:
            stock.SHY += stock.DividendYield
        if stock.BBY:
            stock.SHY += stock.BBY
        stock.save()

def compute_shyrank(snapshot):
    print "Computing SHY rank"
    i = 0
    SHY = None
    stocks = Stock.objects.filter(snapshot=snapshot).order_by("SHY")
    amt = stocks.count()
    for stock in stocks:
        print stock.Ticker
        if stock.SHY != SHY:
            last_rank = i
        stock.SHYRank = Decimal(last_rank)/amt*100
        stock.save()
        i +=1

def compute_evebitdarank(snapshot):
    print "Computing EV/EBITDA rank"
    i = 0
    EVEBITDA = None
    stocks = Stock.objects.filter(snapshot=snapshot).order_by("-EVEBITDA")
    amt = stocks.count()
    for stock in stocks:
        print stock.Ticker
        if stock.EVEBITDA != EVEBITDA:
            last_rank = i
        stock.EVEBITDARank = Decimal(last_rank)/amt*100
        stock.save()
        i +=1

def compute_stockrank(snapshot):
    print "Computing stock rank"
    stocks = Stock.objects.filter(snapshot=snapshot)
    amt = stocks.count()
    for stock in stocks:
        print stock.Ticker
        stock.Rank = stock.PERank+stock.PSRank+stock.PBRank+stock.PFCRank+stock.SHYRank+stock.EVEBITDARank
        stock.save()

def compute_overallrank(snapshot):
    print "Computing Overall rank"
    i = 0
    Rank = None
    stocks = Stock.objects.filter(snapshot=snapshot).order_by("Rank")
    amt = stocks.count()
    for stock in stocks:
        print stock.Ticker
        if stock.Rank != Rank:
            last_rank = i
        stock.OVRRank = Decimal(last_rank)/amt*100
        stock.save()
        i +=1
