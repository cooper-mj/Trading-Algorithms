from datetime import datetime, timedelta

'''
Returns the typical price for a given equity on a given date.
The equity's dataframe is passed into this function (so there is no 
need to specify the equity ticker separately), and this function
returns the average of the high, low, and close on the given date.
'''
def typical_price(df, date):
	date_close = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")]['close'].iloc[0])
	date_low = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")]['low'].iloc[0])
	date_high = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")]['high'].iloc[0])

	return (date_high + date_low + date_close) / 3


'''
Calculates the money flow index to determine buy and sell signals
on a given date.

The money flow index for a given date is calculated as follows:

	Typical Price = (High + Low + Close)/3

	Raw Money Flow = Typical Price x Volume
	Money Flow Ratio = (14-period Positive Money Flow)/(14-period Negative Money Flow)

	Money Flow Index = 100 - 100/(1 + Money Flow Ratio)

If the money flow index for a given date exceeds the sell_bound, then
the equity is considered overbought, and it is a sell signal. Likewise,
if the moeny flow index for the given date exceeds the buy_bound, then the
equity is considered oversold and it is a buy signal.
'''
def money_flow_index(df, date, ticker, unique_properties, price_type='close'):

	period = unique_properties[0]
	sell_bound = unique_properties[1] # Traditionally, the sell bound is 80
	buy_bound = unique_properties[2] # Traditionally, the buy bound is 20

	positive_money_flow = 0
	negative_money_flow = 0

	# Confirm that we have sufficient data to look back period days.
	try:
		start_date_of_data = datetime.strptime(df['date'].iloc[0], "%Y-%m-%d")
		delta = date - start_date_of_data
		if delta.days < period:
			raise ValueError("Cannot take an N-day standard deviation from the given date, given this dataset.")
	except ValueError:
		return

	# Starter value of (period + 1) days ago for the below loop.
	try:
		previous_days_typical_price = typical_price(df, date-timedelta(days = period + 1))
	except IndexError:
		return

	# Loop over the past period days - for each day where the typical price exceeds
	# that of the day before it, add that day's money flow to the positive_money_flow
	# variable; for each day where the typical price is below that of the day before it,
	# add that day's money flow to the negative_money_flow variable.
	for day_num in reversed(range(period)):
		iter_date = date-timedelta(days=day_num)
		formatted_date = iter_date.strftime("%Y-%m-%d")

		try:
			iter_date_volume = float(df.loc[df["date"] == iter_date.strftime("%Y-%m-%d")]['volume'].iloc[0])
			iter_raw_money_flow = typical_price(df, iter_date) * iter_date_volume
		except IndexError:
			continue

		if typical_price(df, iter_date) > previous_days_typical_price:
			positive_money_flow += iter_raw_money_flow

		elif typical_price(df, iter_date) < previous_days_typical_price:
			negative_money_flow += iter_raw_money_flow

		else:
			# Then the typical prices are the same; so we discard this date
			continue

		previous_days_typical_price = typical_price(df, iter_date)

	# To avoid divide-by-zero errors - we set money_flow_volume independently
	# if we have no negative money flow for the given period.
	try:
		money_ratio = float(positive_money_flow)/negative_money_flow

		money_flow_volume = 100 - (100 / (1 + money_ratio))
	except ZeroDivisionError:
		money_flow_volume = 100

	if money_flow_volume > sell_bound:
		return "SELL"

	if money_flow_volume < buy_bound:
		return "BUY"

	return


