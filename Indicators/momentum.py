from datetime import datetime, timedelta

'''
Access the price of the given equity N days ago.
'''
def price_N_days_ago(df, N, date, price_type):
	N_days_ago = date-timedelta(days = N)
	try:
		return float(df.loc[df["date"] == N_days_ago.strftime("%Y-%m-%d")][price_type].iloc[0])
	except (KeyError, IndexError):
		raise IndexError("Cannot find price " + str(N) + " days prior to " + str(date.strftime("%Y-%m-%d")) + " in the database.")

'''
Uses a simple momentum indicator to determine buy and sell signals.
The momentum indicator compares the price of the equity on a given date
with its price period (unique_properties[0]) days ago. If the price is
greater than that of period days ago, it indicates that the equity
is likley overbought and is a "SELL" signal; likewise, if the price of the
equity is less than that of period days ago, it is a "BUY" signal.
'''
def momentum(df, date, ticker, unique_properties, price_type='close'):

	period = unique_properties[0]

	try:
		price = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])
	except (KeyError, IndexError):
		# Then we cannot get the price for this date, so we do not make any
		# indicator inferences.
		return

	try:
		prior_price = price_N_days_ago(df, period, date, price_type)
	except IndexError:
		# Then we cannot get the price for this date, so we do not make any
		# indicator inferences.
		return

	momentum = (price / prior_price) * 100

	return "SELL" if momentum > 100 else "BUY"
