from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint
from threading import Thread
from threading import RLock
from threading import current_thread

# Import indicator algorithms
from Indicators import simple_sma
from Indicators import buy_and_hold
from Indicators import stochastic_oscillator
from Indicators import price_crossover
from Indicators import rsi
from Indicators import bollinger_bands
from Indicators import money_flow_index
from Indicators import momentum

# Import buy/sell functions
from buy_sell_multiple import buy_from_cash
from buy_sell_multiple import redistribute_from_equity
from buy_sell_multiple import cash_out_portfolio

'''
Wrapper function for running each indicator on a given equity
on a given date. 

If the indicator indicates the stock should be bought,
it increments buy_sell_count; if the indicator indicates that the stock
should be sold, it decrements buy_sell_count. If the indicator is
inconclusive, the function re-applies the indicator to the equity on the
previous day (and repeats this at most signal_date_range times, at which 
point it concludes). This design choice was made since the probability that
multiple indicators would all agree on a single date is rather low; there is
a higher probability they would agree within a range of dates. 
'''
def run_indicator(indicator, data, date, equity, unique_properties, signal_date_range, counter):

	indicator_date_range = [date - timedelta(days = x) for x in range(0, signal_date_range)]

	# We invert the indicator_date_range so that the most recent indication (on which the loop
	# would short circuit) is the first one read, which is likely to be most accurate
	# given the data.
	for range_date in reversed(indicator_date_range):

		# We short citcuit this loop to give a binary view of whether or not we should
		# be buying or selling this equity. If, for example, an indicator indicated
		# "SELL" for 8 days in a row, we don't want this repeated "SELL" value to skew
		# our count value. Consistency of a result over time does not imply that we are
		# more sure of that result on the given date.

		if indicator(data, date, equity, unique_properties) == "SELL":
			lock.acquire()
			counter[0] -= 1
			lock.release()
			return

		elif indicator(data, date, equity, unique_properties) == "BUY":
			lock.acquire()
			counter[0] += 1
			lock.release()
			return

'''
Upon being passed in an equity, its data, and a set of indicators,
this function starts one thread per indicator, then applies each 
indicator over a range of dates to the equity (each in its own 
thread), starting on the current day, according to the application
sequence described above in run_indicator.

run_indicator increments/decrements buy_sell_count (incrementing for each
indicator that returns "BUY" on the equity over the given date range, 
decrementig for each indicator that returns "SELL" on the equity over the
given date range). This function waits for all threads to finish, then, 
when a final value for buy_sell_count has been determined, it returns 
buy_sell_count.
'''
def find_buy_sell_count(equity, equity_data, indicators_to_use, date, signal_date_range):
	buy_sell_count = [0] # This count increases with each "BUY"; decreases with each "SELL"; it is a list
						 # so that it may be passed into child functions and incremented/decremented within
						 # those functions.
	threads = []

	# Locks access to buy_sell_count to avoid race conditions (not that any race
	# conditions *should* occur without the lock, but this is mostly just to be
	# extra safe).
	global lock
	lock = RLock()

	for indicator in indicators_to_use.keys():
		t = Thread(target = run_indicator, args = (indicator, equity_data[equity], date, equity, indicators_to_use[indicator], signal_date_range, buy_sell_count))
		threads.append(t)
		t.start()

	for thread in threads:
		# Only proceed once all the child threads have concluded and we have a final
		# number for buy_sell_count
		thread.join()

	return buy_sell_count[0]


'''
Uses a simple trading strategy to manage a portfolio of capital starting_capital
between the dates start_date and end_date. It trades multiple equities (specified
within the equities list parameter), and uses the indicators in the indicators
parameter to determine "BUY" and "SELL" signals.

On a given date, this simulator checks the equities in the equities list parameter
for their respective "BUY" and "SELL" signals, weighted by the number of indicators
which agree on "BUY"/"SELL" signals going back by range (parameter) days.

If an equity is found to be weighted in favour of "SELL", rather than cashing out,
this algorithm first checks to see if there is an equity weighted in favour of "BUY"
in the given time range. If there is, then the money is transferred to from the
"SELL" equity to the "BUY" one.
'''
def multiple_equity_simulator(starting_capital, signal_date_range, start_date, end_date, price_type='close'):

	import collections

	indicators_to_use = {stochastic_oscillator: (20, 80, 14), simple_sma: (30, 90), price_crossover: (30,), rsi: (30, 70, 30), price_crossover: (90,), momentum: (14,)}
	
	# List of equities to trade between
	equities = ["AMZN", "FOXF", "BLFS", "ITI", "CFFI"]

	# Dictionary mapping each equity with its historical stock data
	equity_data = {ticker: get_historical_data(ticker, start=start_date, end=end_date, output_format='pandas') for ticker in equities}

	for equity in equity_data:
		df = equity_data[equity]
		df.index.name = 'date'
		df.reset_index(inplace=True)

	date_range = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]

	capital = starting_capital

	portfolio = {key: 0 for key in equities} # Stores the number of shares of each equity that we hold

	# I am concerned by this quadrouple for loop and am actively considering workarounds
	for date in date_range:

		equities_signals = {key: 0 for key in equities} # Stores the buy/sell count for each equity

		for equity in equities:
			equities_signals[equity] = find_buy_sell_count(equity, equity_data, indicators_to_use, date, signal_date_range)

		# Find the N most buyable equities
		most_buyable_equity = max(equities_signals, key=equities_signals.get)
		N = sum(1 for count in equities_signals.values() if count == equities_signals[most_buyable_equity])
		most_buyable_equities = sorted(equities_signals, key=equities_signals.get, reverse=True)[:N]

		# If equities_signals[most_buyable_equity] <= 0, then we want to sell 
		# our most buyable equity! Instead of putting money into this equity, we should
		# cash out - since we would not expect to make money with any investment in this
		# case. To indicate this, we set the boolean sell_for_cash.
		sell_for_cash = True if equities_signals[most_buyable_equity] < 0 else False

		for equity in portfolio.keys():

			if capital > 0 and not sell_for_cash:
				# Since we have cash, and there are equities which we predict will
				# rise, we evenly distribute the cash into the N most buyable
				# equities.
				capital = buy_from_cash(portfolio, capital, most_buyable_equities, equity_data, date, price_type)

			if equities_signals[equity] < 0 and portfolio[equity] > 0:
				# This means we have a net "SELL" signal on this equity from the
				# given equities, and we own some of the given equity - therefore, we must sell.

				if sell_for_cash:
					# If no equity has a net "BUY" signal, we exchange this equity for cash.
					capital += portfolio[equity] * sell_price
					print(date.strftime("%Y-%m-%d") + " : cashing out " + str(portfolio[equity]) + " shares of " + equity + " for " + str(portfolio[equity] * sell_price) + " dollars.")

				else:
					# If other equities have net "BUY" signals, we sell, then redistribute the
					# capital from this equity into the most buyable ones in the portfolio.
					redistribute_from_equity(portfolio, equity, equity_data, most_buyable_equities, date, price_type)
					

	# We have iterated over all the dates of our time range - at this point, we finally
	# cash out our portfolio.
	cash_out_portfolio(portfolio, date, equity_data, end_date, price_type, capital)


if __name__ == "__main__":

	# Launch interface

	defaults = input("Run with default settings? (y/n): ")
	while not defaults.lower() in ["y", "n"]:
		print("You did not enter a valid response.")
		defaults = input("Run with default settings? (y/n): ")

	if defaults.lower() == "y":
		multiple_equity_simulator(1000, 7, datetime(2015, 1, 25), datetime(2015, 7, 31))

	elif defaults.lower() == "n":
		user_input = []
		print("Please enter syntactically valid Python code on the following lines, to call the desired simulator with your desired parameters.")
		command = input("")
		user_input.append(command)
		while not command == "":
			command = input("")
			user_input.append(command)

		for command in user_input:
			exec(command)

