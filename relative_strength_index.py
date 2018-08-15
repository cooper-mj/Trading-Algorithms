from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

'''
Calculates the relative strength index from the data.
'''
def relative_strength_index(period, dataframe, date, start_date):
	# Check to make sure we can determine the relative strength index from
	# period days ago with the data given - e.g. we can't determine RSI with
	# a 90-day period if we only have data for the past 5 days.
	delta = date - start_date
	if delta.days < period:
		return -1

	sma_start_date = date-timedelta(days=period)
	formatted_sma_start_date = sma_start_date.strftime("%Y-%m-%d")
	formatted_end_date = date.strftime("%Y-%m-%d")
	rows = dataframe[(dataframe['date'] > formatted_sma_start_date) & (dataframe['date'] <= formatted_end_date)]

	average_gain = (len(rows[(rows['open'] > rows['close'])]))	# Number of days where stock went up in price
	average_loss = (len(rows[(rows['open'] < rows['close'])]))	# Number of days where stock went down in price

	return 100 - (float(100) / (1 + (float(average_gain)/float(average_loss))))	# RSI formula

'''
Uses relative strength index indicator to determine buy and sell signals, and managers a
portfolio of initial capital starting_capital accordingly.

When the relative strength index crosses below the buy_bound, it indicates the security is 
underbought, and so is a buy signal. Likewise, when the relative strength index 
crosses above the sell_bound, it indicates that the security is overbought, and so is 
a sell signal.

This algorithm purchases as many shares as possible on a buy signal, and holds until 
a sell signal, at which point it cashes out all the shares for liquid capital. This
repeats until we have reached the final date of the simulation, at which point,
the entire portfolio is cashed out and profits/losses are calculated accordingly.

This algorithm can buy and sell using prices from the set {open, high, low, close}.
'''
def rsi(starting_capital, period, sell_bound, buy_bound, ticker, start_date, end_date, price_type='close'):

	print("")
	cprint("RSI Trading Algorithm:", attrs=['underline', 'bold'])
	cprint("Period: " + str(period) + " days.", color='cyan')
	cprint("Sell Bound: " + str(sell_bound), color='cyan')
	cprint("Buy Bound: " + str(buy_bound), color='cyan')

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

		rsi = relative_strength_index(period, df, date, start_date)

		if rsi == -1:
			# Then we can't get an appropriate relative strength indicator - we are probably too early in the process
			continue

		if rsi > sell_bound:
			# If RSI > selling bound - sell signal
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


		elif rsi < buy_bound:
			# If RSI < buying bound - buy signal
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
