from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta

'''
Returns an N-day simple moving average from date, using price_type
to determine the daily pricing to add into the average (price_type is in the 
set {open, high, low, close}).
'''
def N_day_sma(N, df, date, price_type):
	# Check to make sure we can take an N day standard deviation with the data
	# given - e.g. we can't take a 20 day standard deviation if we only have data
	# for the past 5 days.
	start_date_of_data = datetime.strptime(df['date'].iloc[0], "%Y-%m-%d")
	delta = date - start_date_of_data
	if delta.days < N:
		raise ValueError("Cannot take an N-day standard deviation from the given date, given this dataset.")

	sma_start_date = date-timedelta(days=N)
	formatted_sma_start_date = sma_start_date.strftime("%Y-%m-%d")
	formatted_end_date = date.strftime("%Y-%m-%d")
	rows = df[(df['date'] > formatted_sma_start_date) & (df['date'] <= formatted_end_date)]

	return rows[price_type].mean()


'''
Uses two simple moving averages to determine buy and sell signals on a given date.

When the shorter-term moving average crosses above the longer-term moving average,
it indicates the trend is shifting upwards, and so is a buy signal. Likewise, when the 
shorter-term moving average crosses below the longer-term moving average, it indicates
the trend is shifting downwards, and so is a sell signal.
'''
def simple_sma(df, date, ticker, unique_properties, price_type='close'):

	short_term_N = unique_properties[0]
	long_term_N = unique_properties[1]

	try:
		price = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])

	except (KeyError, IndexError):
		return

	try:
		short_term_sma = N_day_sma(short_term_N, df, date, price_type)
		long_term_sma = N_day_sma(long_term_N, df, date, price_type)
	except ValueError:
		# We could not get an N-day standard deviaion or SMA from the given data - the data did not provide
		# sufficient past references to compute the necessary value.
		return

	if short_term_sma > long_term_sma:
		# If short_term > long_term - sell signal
		return "SELL"

	else:
		# If long_term > short_term - buy signal
		return "BUY"

	return