from datetime import datetime
from datetime import timedelta
from simple_sma import N_day_sma

'''
Calculates the N-day standard deviation of price. Uses price_type to
determine which daily price should be used to calculate the standard
deviation, where price_type is a member of the set {open, high, low, 
close}.
'''
def N_day_price_stddev(N, dataframe, date, price_type):
	# Check to make sure we can take an N day standard deviation with the data
	# given - e.g. we can't take a 20 day standard deviation if we only have data
	# for the past 5 days.
	start_date_of_data = datetime.strptime(dataframe['date'].iloc[0], "%Y-%m-%d")
	delta = date - start_date_of_data
	if delta.days < N:
		raise ValueError("Cannot take an N-day standard deviation from the given date, given this dataset.")

	stddev_start_date = date-timedelta(days=N)
	formatted_stddev_start_date = stddev_start_date.strftime("%Y-%m-%d")
	formatted_end_date = date.strftime("%Y-%m-%d")
	rows = dataframe[(dataframe['date'] > formatted_stddev_start_date) & (dataframe['date'] <= formatted_end_date)]

	return rows[price_type].std()

'''
Uses Bollinger Bands to determine buy and sell signals of a given equity on a
given date.

When the price crosses below the lower Bollinger Band, it indicates the trend is 
shifting upwards, and so is a buy signal. Likewise, when the price crosses above the
upper Bollinger Band, it indicates the trend is shifting downwards, and so is a sell signal.
'''
def bollinger_bands(df, date, ticker, unique_properties, price_type='close'):
	# Unique properties is a tuple containing parameters that vary from indicator to
	# indicator; in the case of the implementation of Bollinger Bands, unique_properties
	# contains the period (N, for the N-day SMA and standard deviation), and the
	# coefficient for the standard deviation.
	period = unique_properties[0]
	stddev_coefficient = unique_properties[1]

	try:
		price = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])

	except (KeyError, IndexError):
		return

	try:
		# Calculate the Bollinger Bands at the given date, with the given parameters
		upper_band = N_day_sma(period, df, date, price_type) + (stddev_coefficient * N_day_price_stddev(period, df, date, price_type))
		lower_band = N_day_sma(period, df, date, price_type) - (stddev_coefficient * N_day_price_stddev(period, df, date, price_type))
	except ValueError:
		# We could not get an N-day standard deviaion or SMA from the given data - the data did not provide
		# sufficient past references to compute the necessary value.
		return

	if price > upper_band:
		# If price is above the upper Bollinger Band - sell signal
		return "SELL"

	elif price < lower_band:
		# If price is below the lower Bollinger Band - buy signal
		return "BUY"

	return


