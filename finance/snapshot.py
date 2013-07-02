import requests
import csv
from models import Stock, Snapshot
import yql
import pdb
from datetime import datetime
from decimal import Decimal
import time

#URL = 'http://finviz.com/screener.ashx?v=152&f=cap_smallover&ft=4&c=0,1,2,6,7,10,11,13,14,45,65'

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
            #query = 'select EBITDA from yahoo.finance.quotes where symbol=@symbol limit 1'
            #ebitda = y.execute(query, {"symbol": stock.Ticker}, env="http://www.datatables.org/alltables.env").one()["EBITDA"]
            #if ebitda:
            #    if ebitda == "0":
            #        stock.EBITDA = 0
            #    else:
            #        stock.EBITDA = ebitda[:-1]
            #        stock.EBITDAScale = ebitda[-1]
            stock.save()
        except:
            pdb.set_trace()
            

    import_ebitda(snapshot)

    import_buyback_yield(snapshot)

def import_ebitda(snapshot, startwith=None):
    # Download EBITDA value from yahoo finance
    print "Importing EBITDA"
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
        nquery = 'select symbol, EBITDA from yahoo.finance.quotes where symbol in ({0})'.format('"'+('","'.join(tickers[i:i+step-1])+'"'))
        ebitdas = y.execute(nquery, env="http://www.datatables.org/alltables.env")
        if ebitdas.results:
            for row in ebitdas.results["quote"]:
                print row["symbol"]
                ebitda = row["EBITDA"]
                if ebitda:
                    stock = Stock.objects.get(snapshot=snapshot, Ticker=row["symbol"])
                    if ebitda == "0":
                        stock.EBITDA = 0
                    elif ebitda[-1] == "B":
                        stock.EBITDA = Decimal(ebitda[:-1])*100000000000
                    elif ebitda[-1] == "M":
                        stock.EBITDA = Decimal(ebitda[:-1])*10000000
                    elif ebitda[-1] == "K":
                        stock.EBITDA = Decimal(ebitda[:-1])*1000
                    else:
                        stock.EBITDA = ebitda
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

def compute_rank(snapshot):

    print "Computing PE rank"
    i = 0
    PE = None
    stocks = Stock.objects.filter(snapshot=snapshot,PE__isnull=False).order_by("-PE")
    amt = len(stocks)
    for stock in stocks:
        print stock.Ticker
        if stock.PE != PE:
            last_rank = i
        stock.PERank = (last_rank/amt+1)*100
        stock.save()
        i +=1

    print "Computing PS rank"
    i = 0
    PS = None
    stocks = Stock.objects.filter(snapshot=snapshot,PS__isnull=False).order_by("-PS")
    for stock in stocks:
        print stock.Ticker
        if stock.PS != PS:
            last_rank = i
        stock.PSRank = (last_rank/amt+1)*100
        stock.save()
        i +=1

    print "Computing PB rank"
    i = 0
    PB = None
    stocks = Stock.objects.filter(snapshot=snapshot,PB__isnull=False).order_by("-PB")
    for stock in stocks:
        print stock.Ticker
        if stock.PB != PB:
            last_rank = i
        stock.PBRank = (last_rank/amt+1)*100
        stock.save()
        i +=1

    print "Computing PFS rank"
    i = 0
    PFS = None
    stocks = Stock.objects.filter(snapshot=snapshot,PFreeCashFlow__isnull=False).order_by("-PFreeCashFlow")
    for stock in stocks:
        print stock.Ticker
        if stock.PFreeCashFlow != PFS:
            last_rank = i
        stock.PFSRank = (last_rank/amt+1)*100
        stock.save()
        i +=1

    print "Computing SHY"
    for stock in Stock.objects.filter(snapshot=snapshot);
        stock.SHY = stock.DividendYield + stock.BBY
        stock.save()

    print "Computing SHY rank"
    i = 0
    SHY = None
    stocks = Stock.objects.filter(snapshot=snapshot,SHY__isnull=False).order_by("SHY")
    for stock in stocks:
        print stock.Ticker
        if stock.SHY != SHY:
            last_rank = i
        stock.SHYRank = (last_rank/amt)*100
        stock.save()
        i +=1

    print "Computing EV/EBITDA"

    print "Computing EV/EBITDA rank"



if __name__ == "__main__":
    main()
