from datetime import datetime
from datetime import timedelta


'''
Uses a stochastic oscillator to determine buy/sell signals for a given equity on
a certain day. It calculates the highest high and lowest low in a given period
(the period length is passed in through the unique_properties tuple), then
calculates the K line according to those values. The K line is then compared
against buy and sell thresholds (also passed in through unique_properties) to
determine whether to buy and/or sell on the given date.
'''
def stochastic_oscillator(df, date, ticker, unique_properties, price_type='close'):
	low_reading_bound = unique_properties[0]
	high_reading_bound = unique_properties[1]
	period_length = unique_properties[2]

	try:
		price = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])
		current_close = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")]['close'].iloc[0])
	except (KeyError, IndexError):
		# This date isn't in the database, so we can't calculate price, current_close
		return

	period_start = date-timedelta(days=period_length)
	formatted_period_start = period_start.strftime("%Y-%m-%d")
	rows = df[(df['date'] > formatted_period_start) & (df['date'] <= date.strftime("%Y-%m-%d"))]

	lowest_low_in_period = rows['low'].min()
	highest_high_in_period = rows['high'].max()

	# Check to make sure K won't give a divide by zero problem
	if (current_close == highest_high_in_period):
		return
	K = abs((current_close - lowest_low_in_period) / (current_close - highest_high_in_period))

	if K < low_reading_bound:
		# If K < low_reading_bound, this is a buy signal
		return "BUY"

	elif K > high_reading_bound:
		# If K > high_reading_bound, this is a sell signal
		return "SELL"