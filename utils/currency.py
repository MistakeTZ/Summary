import pandas as pd
import requests
from matplotlib import pyplot as plt
from os import path
import datetime
import dateutil.relativedelta

def make_graph(company, company_name):
    plt.clf()
    
    till = datetime.datetime.now()
    from_ = till + dateutil.relativedelta.relativedelta(months=-2, days=-15)

    j = requests.get('http://iss.moex.com/iss/engines/stock/markets/shares/securities/{}/candles.json?from={}&till={}&interval=7'.format(
        company, from_.strftime("%Y-%m-%d"), till.strftime("%Y-%m-%d"))).json()
    data = [{k : r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
    frame = pd.DataFrame(data)

    y = list(frame['close'])
    x = [el[8:10]+"." + el[5:7] for el in list(frame['end'])]

    since = list(frame['end'])[0][8:10] + "." + list(frame['end'])[0][5:7]
    to = list(frame['end'])[-1][8:10] + "." + list(frame['end'])[-1][5:7]
    plt.title(company_name + " за период с " + since + " по " + to)
    
    plt.plot(x, y)
    plt.savefig(path.join("temp", "shares.png"))

    return y[-1]
