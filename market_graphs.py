from iexfinance import get_historical_data
from datetime import datetime
import matplotlib.pyplot as plt

from simple_sma import N_day_sma
from relative_strength_index import relative_strength_index

'''
Imports historical stock pricing data for the ticker stock within the range [start_date, 
end_date], then uses matplotlib.pyplot to graph the price of the stock with respect 
to the date. This function can graph daily prices from the set {open, high, low, close}.
'''
def price_graph(start_date, end_date, ticker, price_type="close"):

	# Import stock data in the desired date range
	df = get_historical_data(ticker, start=start_date, end=end_date, output_format='pandas')
	df.index.name = 'date'
	df.reset_index(inplace=True)

	plt.plot(df['date'], df[price_type])	

'''
Calculates the N-day SMA for the ticker stock within the range [start_date, 
end_date], then uses matplotlib.pyplot to graph the N-day SMA of the stock with 
respect to the date. This function can calculate the SMA using daily prices 
from the set {open, high, low, close}.
'''
def sma_graph(N, start_date, end_date, ticker, price_type="close"):

	df = get_historical_data(ticker, start=start_date, end=end_date, output_format='pandas')
	df.index.name = 'date'
	df.reset_index(inplace=True)

	df['SMA'] = df['date'].apply(lambda x: N_day_sma(N, df, datetime.strptime(str(x), "%Y-%m-%d"), start_date, price_type))

	plt.plot(df['date'], df['SMA'])

'''
Calculates the relative strength index daily wihtin the range [start_date,
end_date], then uses matplotlib.pyplot to graph the relative strength index,
along with buy and sell thresholds.
'''
def rsi_graph(period, start_date, end_date, sell_bound, buy_bound, ticker):

	df = get_historical_data(ticker, start=start_date, end=end_date, output_format='pandas')
	df.index.name = 'date'
	df.reset_index(inplace=True)

	df['RSI'] = df['date'].apply(lambda x: relative_strength_index(period, df, datetime.strptime(str(x), "%Y-%m-%d"), start_date))

	plt.plot(df['date'], df['RSI'])
	plt.axhline(y = sell_bound)
	plt.axhline(y = buy_bound)


if __name__ == "__main__":
	#Sample use
	price_graph(datetime(2015, 1, 25), datetime(2018, 8, 1), "GS")
	#sma_graph(20, datetime(2015, 1, 25), datetime(2018, 8, 1), "GS")
	rsi_graph(14, datetime(2015, 1, 25), datetime(2018, 8, 1), 70, 30, "GS")

	plt.show()


