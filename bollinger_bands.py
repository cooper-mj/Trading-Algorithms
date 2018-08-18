from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

from simple_sma import N_day_sma
from buy_sell import sell
from buy_sell import buy

'''
Calculates the N-day standard deviation of price. Uses price_type to
determine which daily price should be used to calculate the standard
deviation, where price_type is a member of the set {open, high, low, 
close}.
'''
def N_day_price_stddev(N, dataframe, date, start_date, price_type):
	# Check to make sure we can take an N day standard deviation with the data
	# given - e.g. we can't take a 20 day standard deviation if we only have data
	# for the past 5 days.
	delta = date - start_date
	if delta.days < N:
		return -1

	sma_start_date = date-timedelta(days=N)
	formatted_sma_start_date = sma_start_date.strftime("%Y-%m-%d")
	formatted_end_date = date.strftime("%Y-%m-%d")
	rows = dataframe[(dataframe['date'] > formatted_sma_start_date) & (dataframe['date'] <= formatted_end_date)]

	return rows[price_type].std()

'''
Uses Bollinger Bands to determine buy and sell signals, and managers a portfolio of 
initial capital starting_capital accordingly.

When the price crosses below the lower Bollinger Band, it indicates the trend is 
shifting upwards, and so is a buy signal. Likewise, when the price crosses above the
upper Bollinger Band, it indicates the trend is shifting downwards, and so is a sell signal.

This algorithm purchases as many shares as possible on a buy signal, and holds until 
a sell signal, at which point it cashes out all the shares for liquid capital. This
repeats until we have reached the final date of the simulation, at which point,
the entire portfolio is cashed out and profits/losses are calculated accordingly.

This algorithm can compute simple moving averages using {open, high, low, close} prices,
though traditionally Bollinger Bands are computed using the closing price.
'''
def bollinger_bands(starting_capital, period, stddev_coefficient, ticker, start_date, end_date, price_type='close'):

	print("")
	cprint("Bollinger Bands Trading Algorithm:", attrs=['underline', 'bold'])
	cprint("Period: " + str(period) + " days.", color='cyan')

	# Acknowledgement: Hugo Rodger Brown (StackOverFlow) for this constructor notation: https://stackoverflow.com/questions/7274267/print-all-day-dates-between-two-dates
	date_range = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]

	# Import stock data in the desired date range
	df = get_historical_data(ticker, start=start_date, end=end_date, output_format='pandas')
	df.index.name = 'date'
	df.reset_index(inplace=True)

	capital = starting_capital
	num_shares = 0
	liquid = True
	
	previous_price = 0
	correct = [0, 0]

	for date in date_range:
		try:
			price = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])

		except (KeyError, IndexError):
			continue

		upper_band = N_day_sma(period, df, date, start_date, price_type) + (stddev_coefficient * N_day_price_stddev(period, df, date, start_date, price_type))
		lower_band = N_day_sma(period, df, date, start_date, price_type) - (stddev_coefficient * N_day_price_stddev(period, df, date, start_date, price_type))

		if price > upper_band:
			# If price is above the upper Bollinger Band - sell signal
			if not liquid:
				sell_data = sell(liquid, date, ticker, capital, num_shares, price, previous_price, correct)
				liquid = sell_data[0]
				capital = sell_data[1]
				num_shares = sell_data[2]


		elif price < lower_band:
			# If price is below the lower Bollinger Band - buy signal
			if liquid:
				buy_data = buy(liquid, date, ticker, capital, num_shares, price, previous_price, correct)
				liquid = buy_data[0]
				capital = buy_data[1]
				num_shares = buy_data[2]

		previous_price = price

	if capital == 0:
		# Sell the remaining shares usig the final date's price
		capital = num_shares * previous_price
		num_shares = 0

	cprint("Finished with " + str(round(capital, 2)) + " dollars.", color='cyan')
	cprint("Made money in " + str(correct[0]) + " out of " + str(round(correct[1], 2)) + " decisions. Accuracy: " + str(float(correct[0])/correct[1]), color='cyan')
