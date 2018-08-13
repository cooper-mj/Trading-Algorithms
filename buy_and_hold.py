from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

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
