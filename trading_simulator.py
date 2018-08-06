
from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

# '''
# Returns the N-day simple moving average for the given
# ticker on the given date. Date must be passed in as a
# datetime object. Price type must be in the set
# { 'open', 'high', 'low', 'close' }.
# '''
# def N_day_sma(N, ticker, date, price_type='close'):
# 	start_date = date - timedelta(days=N)
# 	end_date = date
# 	try:
# 		df = get_historical_data(ticker, start=start_date, end=end_date, output_format='pandas')
# 		return df[price_type].mean()
# 	except ValueError:
# 		print("The average starting at this date falls outside the 5-year limit on historical data that this API provides.")
# 		return -1

def N_day_sma_from_dataframe(N, dataframe, date, start_date, price_type):
	# Check to make sure we can take an N day moving average with the data
	# given - e.g. we can't take a 90-day average if we only have data
	# for 5 days.
	delta = date - start_date
	if delta.days < N:
		return -1

	sma_start_date = date-timedelta(days=N)
	formatted_sma_start_date = sma_start_date.strftime("%Y-%m-%d")
	formatted_end_date = date.strftime("%Y-%m-%d")
	rows = dataframe[(dataframe['date'] > formatted_sma_start_date) & (dataframe['date'] <= formatted_end_date)]

	return rows[price_type].mean()


'''
E.g. if I was to 
'''
def simple_sma_trade(starting_capital, short_term_N, long_term_N, ticker, start_date, end_date, price_type='close'):

	print("")
	cprint("SMA Trading Algorithm:", attrs=['underline', 'bold'])
	cprint("Short term SMA: " + str(short_term_N) + " days.", color='cyan')
	cprint("Long term SMA: " + str(long_term_N) + " days.", color='cyan')

	# Credit to Hugo Rodger Brown (StackOverFlow) for this constructor notation: https://stackoverflow.com/questions/7274267/print-all-day-dates-between-two-dates
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
			#at[date.strftime("%Y-%m-%d"), price_type]
		except (KeyError, IndexError):
			continue

		short_term_sma = N_day_sma_from_dataframe(short_term_N, df, date, start_date, price_type)
		long_term_sma = N_day_sma_from_dataframe(long_term_N, df, date, start_date, price_type)

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


def buy_and_hold(starting_capital, ticker, start_date, end_date, price_type='close'):
	
	print("")
	cprint("Buy-And-Hold Algorithm:", attrs=['underline', 'bold'])

	df = get_historical_data(ticker, start=start_date-timedelta(days=1), end=end_date+timedelta(days=1), output_format='pandas')
	df.index.name = 'date'
	df.reset_index(inplace=True)

	# Get start and end dates, and prices associated with each
	try:
		start_price = float(df.loc[df["date"] == start_date.strftime("%Y-%m-%d")][price_type].iloc[0])
	except (KeyError, IndexError):
		new_start_date = min(date for date in df["date"] if date > start_date.strftime("%Y-%m-%d"))
		print("Your selected start date was not found in the database. Starting on " + new_start_date + " instead of " + start_date.strftime("%Y-%m-%d") + ".")
		start_price = float(df.loc[df["date"] == new_start_date][price_type].iloc[0])

	try:
		end_price = float(df.loc[df["date"] == end_date.strftime("%Y-%m-%d")][price_type].iloc[0])
	except (KeyError, IndexError):
		new_end_date = max(date for date in df["date"] if date < end_date.strftime("%Y-%m-%d"))
		print("Your selected end date was not found in the database. Ending on " + new_end_date + " instead of " + end_date.strftime("%Y-%m-%d") + ".")
		end_price = float(df.loc[df["date"] == new_end_date][price_type].iloc[0])

	start_date = start_date.strftime("%Y-%m-%d")
	end_date = end_date.strftime("%Y-%m-%d")
	# Buy initially
	capital = starting_capital
	num_shares = float(capital) / start_price
	buy_msg = colored("Buying " + str(round(num_shares, 2)) + " at " + str(round(start_price, 2)) + " for " + str(round(capital, 2)), 'green')
	print(start_date + " : " + buy_msg)
	capital = 0


	# Sell finally
	capital = num_shares * end_price
	sell_msg = colored("Selling " + str(round(num_shares, 2)) + " at " + str(round(end_price, 2)) + " for " + str(round(capital, 2)), 'red')
	print(end_date + " : " + sell_msg)
	num_shares = 0

	cprint("Finished with " + str(capital) + " dollars.", color='cyan')


def stochastic_oscillator(starting_capital, ticker, start_date, end_date, period_length, price_type='close', low_reading_bound=20, high_reading_bound=80):

	print("")
	cprint("Stochastic Oscillator Algorithm:", attrs=['underline', 'bold'])
	cprint("Period Length: " + str(period_length) + " days.", color='cyan')

	df = get_historical_data(ticker, start=start_date-timedelta(days=1), end=end_date+timedelta(days=1), output_format='pandas')
	df.index.name = 'date'
	df.reset_index(inplace=True)

	capital = starting_capital
	num_shares = 0
	liquid = True

	previous_price = 0
	correct = [0, 0]

	date_range = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]

	for date in date_range:
		try:
			price = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])
			current_close = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")]['close'].iloc[0])

			#at[date.strftime("%Y-%m-%d"), price_type]
		except (KeyError, IndexError):
			continue

		period_start = start_date-timedelta(days=period_length)
		formatted_period_start = period_start.strftime("%Y-%m-%d")
		rows = df[(df['date'] > formatted_period_start) & (df['date'] <= date.strftime("%Y-%m-%d"))]

		lowest_low_in_period = rows['low'].min()
		highest_high_in_period = rows['high'].max()

		# Check to make sure K won't give a divide by zero problem
		if (current_close == highest_high_in_period):
			continue
		K = abs((current_close - lowest_low_in_period) / (current_close - highest_high_in_period))
		# Need to get D, 3-day-SMA of K

		if K < low_reading_bound:
			# Buy signal
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
		
		elif K > high_reading_bound:
			# Sell signal
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

	if capital == 0:
		# Sell the remaining shares usig the final date's price
		capital = num_shares * previous_price
		num_shares = 0

	cprint("Finished with " + str(round(capital, 2)) + " dollars.", color='cyan')
	cprint("Made money in " + str(correct[0]) + " out of " + str(round(correct[1], 2)) + " decisions. Accuracy: " + str(float(correct[0])/correct[1]), color='cyan')


if __name__ == "__main__":

	simple_sma_trade(1000, 30, 90, "SVU", datetime(2015, 1, 25), datetime(2018, 8, 1))
	buy_and_hold(1000, "SVU", datetime(2015, 1, 25), datetime(2018, 8, 1))
	stochastic_oscillator(1000, "SVU", datetime(2015, 1, 25), datetime(2018, 8, 1), 14)

