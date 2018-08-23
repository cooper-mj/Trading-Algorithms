from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

'''
Calculates the relative strength index of the equity on a given date from
the data.
'''
def relative_strength_index(period, dataframe, date):
	# Check to make sure we can determine the relative strength index from
	# period days ago with the data given - e.g. we can't determine RSI with
	# a 90-day period if we only have data for the past 5 days.
	start_date = datetime.strptime(dataframe['date'].iloc[0], "%Y-%m-%d")
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
Uses relative strength index indicator to determine buy and sell signals on a given
date.

When the relative strength index crosses below the buy_bound, it indicates the security is 
underbought, and so is a buy signal. Likewise, when the relative strength index 
crosses above the sell_bound, it indicates that the security is overbought, and so is 
a sell signal.
'''
def rsi(df, date, ticker, unique_properties, price_type='close'):
	period = unique_properties[0]
	sell_bound = unique_properties[1]
	buy_bound = unique_properties[2]

	try:
		price = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])

	except (KeyError, IndexError):
		return

	rsi = relative_strength_index(period, df, date)

	if rsi == -1:
		# Then we can't get an appropriate relative strength indicator - we are probably too early in the process
		return

	if rsi > sell_bound:
		# If RSI > selling bound - sell signal
			return "SELL"

	elif rsi < buy_bound:
		# If RSI < buying bound - buy signal
		return "BUY"

	return