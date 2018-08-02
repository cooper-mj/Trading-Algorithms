

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import datetime

from termcolor import colored, cprint
import sys


'''
Takes in an API key and a ticker symbol; returns a dictionary
mapping dates to N-day simple moving averages for each date.
'''
def N_day_sma(N, API_key, ticker, price_time):
	#ti = TechIndicators(key=API_key)
	N_day, N_md = ti.get_sma(ticker, 'daily', N, price_time)

	N_sma = {}
	for day in N_day:
		date = datetime.datetime.strptime(day, "%Y-%m-%d").date()
		N_sma[date] = float(N_day[day]['SMA'])
	return N_sma

def price_data(API_key, ticker, price_time):
	#ts = TimeSeries(key=API_key)
	price, price_md = ts.get_daily(symbol=ticker, outputsize='full')
	price_dict = {}
	for day in price:
		date = datetime.datetime.strptime(day, "%Y-%m-%d").date()
		price_dict[date] = float(price[day][price_time])
	return price_dict

def simple_sma_trade(API_key, starting_capital, ticker):
	'''
	Uses 30 and 90 day simple moving averages to compute buy and sell
	signals. Buys and sells when the buy/sell signal changes. Buys and
	sells full portfolio at each buy/sell signal.
	'''

	thirty_day_sma = N_day_sma(1, API_key, ticker, 'close')
	ninety_day_sma = N_day_sma(2, API_key, ticker, 'close')
	prices = price_data(API_key, ticker, '4. close') # the '4. close' instead of just 'close' is just one of the idiosynchronacies of this library.

	# Ensure that all dates we will be evaluating are valid for 30 day SMA, 90 day SMA, and price tracking
	cumulative_dates = sorted(list(set(thirty_day_sma.keys()) & set(ninety_day_sma.keys()) & set(prices)))

	capital = starting_capital
	num_shares = 0
	status_buy = False
	
	previous_price = 0
	correct = [0, 0]

	print("Ready to trade!")

	for date in cumulative_dates:

		if thirty_day_sma[date] > ninety_day_sma[date]:
			# If thirty_day > ninety_day - sell signal
			if status_buy:
				status_buy = False
				capital = num_shares * prices[date]
				sell_msg = colored("Selling " + str(num_shares) + " at " + str(prices[date]) + " for " + str(capital), 'red')
				print(date + " : " + sell_msg)
				num_shares = 0

				# Check to see if our last decision was the right one
				if prices[date] > previous_price:
					# Check if current price is more than the price we bought for since
					# our last call was a buy
					correct[0] += 1
					correct[1] += 1
				else:
					correct[1] += 1

				previous_price = prices[date]


		else:
			# If ninety_day > thirty_day - buy signal
			if not status_buy:
				status_buy = True
				num_shares = float(capital) / prices[date]
				buy_msg = colored("Buying " + str(num_shares) + " at " + str(prices[date]) + " for " + str(capital), 'green')
				print(date + " : " + buy_msg)
				capital = 0

				# Check to see if our last decision was the right one
				if prices[date] < previous_price:
					# Check if current price is less than price we bought for since
					# our last call was a buy - check if we made money
					correct[0] += 1
					correct[1] += 1
				else:
					correct[1] += 1
	
				previous_price = prices[date]


	if capital == 0:
		# Sell the remaining shares usig the final date's price
		capital = num_shares * prices[cumulative_dates[-1]]
		num_shares = 0

	print("Finished with " + str(capital) + " dollars.")
	print("Made money in " + str(correct[0]) + " out of " + str(correct[1]) + " decisions. Accuracy: " + str(float(correct[0])/correct[1]))

	#buy_and_hold(API_key, starting_capital, ticker)

def buy_and_hold(API_key, starting_capital, ticker):

	prices = price_data(API_key, ticker, '4. close') # the '4. close' instead of just 'close' is just one of the idiosynchronacies of this library.
	cumulative_dates = sorted(prices.keys())

	# Buy initially
	capital = starting_capital
	num_shares = float(capital) / prices[cumulative_dates[0]]
	capital = 0

	# Sell finally
	capital = num_shares * prices[cumulative_dates[-1]]
	num_shares = 0

	print("Finished with " + str(capital) + "dollars.")



def plot_averages():
	from alpha_vantage.timeseries import TimeSeries
	from alpha_vantage.techindicators import TechIndicators
	import datetime
	import matplotlib.pyplot as plt

	#ti = TechIndicators(key="Y9LU3HXNM65GKI9R")
	thirty_day, thirty_md = ti.get_sma('.DJI', 'daily', 30, 'close')
	ninety_day, ninety_md = ti.get_sma('.DJI', 'daily', 90, 'close')

	thirty_dict = {}
	for day in thirty_day:
		date = datetime.datetime.strptime(day, "%Y-%m-%d").date()
		thirty_dict[date] = float(thirty_day[day]['SMA'])

	ninety_dict = {}
	for day in ninety_day:
		date = datetime.datetime.strptime(day, "%Y-%m-%d").date()
		ninety_dict[date] = float(ninety_day[day]['SMA'])

	thirtyday_x, thirtyday_y = zip(*sorted(thirty_dict.items()))
	thirty_day_sma, = plt.plot(thirtyday_x, thirtyday_y, 'r', label="Thirty Day Simple Moving Average")

	ninetyday_x, ninetyday_y = zip(*sorted(ninety_dict.items()))
	ninety_day_sma, = plt.plot(ninetyday_x, ninetyday_y, 'g', label="Ninety Day Simple Moving Average")

	plt.legend(handles=[thirty_day_sma, ninety_day_sma])

	# All the days in the ninety day moving average are in the 30 day one

	# -----
	#ts = TimeSeries(key="Y9LU3HXNM65GKI9R")
	price, price_md = ts.get_daily(symbol='.DJI', outputsize='full')
	# price_x, price_y = zip(*sorted(price.items()))
	price_dict = {}
	for day in price:
		date = datetime.datetime.strptime(day, "%Y-%m-%d").date()
		price_dict[date] = float(price[day]['4. close'])
	
	price_x, price_y = zip(*sorted(price_dict.items()))
	price_sma, = plt.plot(price_x, price_y)

	plt.show()

if __name__ == "__main__":
	API_KEY = sys.argv[1]

	global ti
	ti = TechIndicators(key=API_KEY)
	global ts
	ts = TimeSeries(key=API_KEY)
	
	simple_sma_trade(API_KEY, 1000, ".DJI")
	#plot_averages()


