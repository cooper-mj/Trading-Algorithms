from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

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
		
				previous_price = price

		
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
