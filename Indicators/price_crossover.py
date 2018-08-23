from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from .simple_sma import N_day_sma

'''
Uses a simple moving average price crossover strategy to determine buy 
and sell signals.

When the price is higher than the simple moving average, it indicates that the
price is likely to fall, and so is a sell signal. Likewise, when the price is 
lower than the simple moving average, it indicates that the prices is likely 
to rise, and so is a buy signal.
'''
def price_crossover(df, date, ticker, unique_properties, price_type='close'):

	N = unique_properties[0]

	try:
		price = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])

	except (KeyError, IndexError):
		return

	try:
		sma = N_day_sma(N, df, date, price_type)
	except ValueError:
		# We could not get an N-day standard deviaion or SMA from the given data - the data did not provide
		# sufficient past references to compute the necessary value.
		return

	if sma > price:
		# If SMA > price - sell signal
		return "SELL"

	else:
		# If price > SMA - buy signal
		return "BUY"

	return