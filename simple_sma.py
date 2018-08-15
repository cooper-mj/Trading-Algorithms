from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

'''
Returns an N-day simple moving average from the current date, using price_type
to determine the daily pricing to add into the average (price_type is in the 
set {open, high, low, close}).
'''
def N_day_sma(N, dataframe, date, start_date, price_type):
	# Check to make sure we can take an N day moving average with the data
	# given - e.g. we can't take a 90-day average if we only have data
	# for the past 5 days.
	delta = date - start_date
	if delta.days < N:
		return -1

	sma_start_date = date-timedelta(days=N)
	formatted_sma_start_date = sma_start_date.strftime("%Y-%m-%d")
	formatted_end_date = date.strftime("%Y-%m-%d")
	rows = dataframe[(dataframe['date'] > formatted_sma_start_date) & (dataframe['date'] <= formatted_end_date)]

	return rows[price_type].mean()

'''
Uses two simple moving averages to determine buy and sell signals, and managers a
portfolio of initial capital starting_capital accordingly.

When the shorter-term moving average crosses above the longer-term moving average,
it indicates the trend is shifting upwards, and so is a buy signal. Likewise, when the 
shorter-term moving average crosses below the longer-term moving average, it indicates
the trend is shifting downwards, and so is a sell signal.

This algorithm purchases as many shares as possible on a buy signal, and holds until 
a sell signal, at which point it cashes out all the shares for liquid capital. This
repeats until we have reached the final date of the simulation, at which point,
the entire portfolio is cashed out and profits/losses are calculated accordingly.

This algorithm can compute simple moving averages using {open, high, low, close} prices.
'''
def simple_sma_trade(starting_capital, short_term_N, long_term_N, ticker, start_date, end_date, price_type='close'):

	print("")
	cprint("SMA Trading Algorithm:", attrs=['underline', 'bold'])
	cprint("Short term SMA: " + str(short_term_N) + " days.", color='cyan')
	cprint("Long term SMA: " + str(long_term_N) + " days.", color='cyan')

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

		short_term_sma = N_day_sma(short_term_N, df, date, start_date, price_type)
		long_term_sma = N_day_sma(long_term_N, df, date, start_date, price_type)

		if short_term_sma == -1 or long_term_sma == -1:
			# Then we can't get an N-day SMA - we are probably too early in the process
			continue

		if short_term_sma > long_term_sma:
			# If short_term > long_term - sell signal
			if not liquid:
				liquid = True
				capital = num_shares * price
				sell_msg = colored("Selling " + str(round(num_shares, 2)) + " shares of " + ticker + " at " + str(round(price, 2)) + " for " + str(round(capital, 2)), 'red')
				print(date.strftime("%Y-%m-%d") + " : " + sell_msg)
				num_shares = 0

				# Check to see if our last decision was the right one
				if price > previous_price:
					# Check if current price is less than price we bought for since
					# our last call was a buy - check if we made money
					correct[0] += 1
					correct[1] += 1
				else:
					correct[1] += 1

				previous_price = price


		else:
			# If long_term > short_term - buy signal
			if liquid:
				liquid = False
				num_shares = float(capital) / price
				buy_msg = colored("Buying " + str(round(num_shares, 2)) + " shares of " + ticker + " at " + str(round(price, 2)) + " for " + str(round(capital, 2)), 'green')
				print(date.strftime("%Y-%m-%d") + " : " + buy_msg)
				capital = 0

				# Check to see if our last decision was the right one
				if price < previous_price:
					# Check if current price is less than price we bought for since
					# our last call was a buy - check if we made money
					correct[0] += 1
					correct[1] += 1
				else:
					correct[1] += 1

				previous_price = price

	if capital == 0:
		# Sell the remaining shares usig the final date's price
		capital = num_shares * previous_price
		num_shares = 0

	cprint("Finished with " + str(round(capital, 2)) + " dollars.", color='cyan')
	cprint("Made money in " + str(correct[0]) + " out of " + str(round(correct[1], 2)) + " decisions. Accuracy: " + str(float(correct[0])/correct[1]), color='cyan')
