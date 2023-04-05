import matplotlib.pyplot as plt
from var import data
import datetime as dt

def ts_plot(data):
    fig, ax = plt.subplots(figsize = (16, 9))
    ax.plot(data)
    ax.set_xlabel("Date")
    ax.set_ylabel("Adjusted Closing Price")

end = dt.date.today()
start = end - dt.timedelta(100)

stocks = ["TSLA",]
cd, r, avg = data(stocks, start = start, end = end)
ts_plot(cd)
