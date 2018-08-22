
from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

# Import indicator algorithms
from simple_sma import simple_sma
from buy_and_hold import buy_and_hold
from stochastic_oscillator import stochastic_oscillator
from price_crossover import price_crossover
from relative_strength_index import rsi
from bollinger_bands import bollinger_bands

# Import functions for buying and selling a single equity
from buy_sell_single import sell
from buy_sell_single import buy


from trading_simulator_multiple import multiple_equity_simulator
'''
Prints title and parameter of the indicator being used.
'''
def print_introduction_message(indicator, indicators_to_use):
	print("")

	if indicator == bollinger_bands:
		cprint("Bollinger Bands Trading Algorithm:", attrs=['underline', 'bold'])
		cprint("Period: " + str(indicators_to_use[bollinger_bands][0]) + " days.", 'cyan')

	elif indicator == buy_and_hold:
		cprint("Buy-And-Hold Algorithm:", attrs=['underline', 'bold'])

	elif indicator == price_crossover:
		cprint("Price Crossover Trading Algorithm:", attrs=['underline', 'bold'])
		cprint("SMA: " + str(indicators_to_use[price_crossover][0]) + " days.", 'cyan')

	elif indicator == rsi:
		cprint("RSI Trading Algorithm:", attrs=['underline', 'bold'])
		cprint("Period: " + str(indicators_to_use[rsi][0]) + " days.", color='cyan')
		cprint("Sell Bound: " + str(indicators_to_use[rsi][1]), color='cyan')
		cprint("Buy Bound: " + str(indicators_to_use[rsi][2]), color='cyan')

	elif indicator == simple_sma:
		cprint("Simple SMA Trading Algorithm:", attrs=['underline', 'bold'])
		cprint("Short-term SMA: " + str(indicators_to_use[simple_sma][0]) + " days.", 'cyan')
		cprint("Long-term SMA: " + str(indicators_to_use[simple_sma][1]) + " days.", 'cyan')

	elif indicator == stochastic_oscillator:
		cprint("Stochastic Oscillator Algorithm:", attrs=['underline', 'bold'])
		cprint("Period Length: " + str(indicators_to_use[stochastic_oscillator][2]) + " days.", color='cyan')

'''
Uses a simple trading strategy to manage a portfolio of capital starting_capital
between the dates start_date and end_date. It only trades a single equity, represented
by ticker, and it uses a single indicator at a time to compute "BUY" and "SELL" signals.

Upon receiving the first "BUY" signal in the given date range, the algorithm purchases
as many shares as it can with its given capital. It holds those shares until it receives
a "SELL" signal from the indicator, at which point it liquidates its entire holdings. The
process repeats in this manner until it reaches the end of the date range, at which point
it liquidates any holdings, if it is holding any equity on that date.
'''
def single_equity_simulator(starting_capital, ticker, start_date, end_date, price_type='close'):

	# Indicators are added to a dictionary called indicators_to_use. The key of the dictionary
	# is the indicator function which computes "BUY" and "SELL" signals; the value is a tuple
	# containing parameters for the indicator. These parameters vary from indicator to indicator.
	# For example, the price_crossover indicator requires a single parameter in its tuple (the
	# duration of SMA to use), while the rsi indicator requires three (the duration of SMA to
	# use, the sell bound, and the buy bound). At the top of each indicator function, these
	# values are extracted. Peruse the code for your desired indicator function to see exactly
	# which parameters it takes into its tuple.
	indicators_to_use = {stochastic_oscillator: (20, 80, 14), simple_sma: (30, 90), buy_and_hold: (), price_crossover: (30,), rsi: (30, 70, 30)}

	for indicator in indicators_to_use.keys():

		print_introduction_message(indicator, indicators_to_use)

		# Acknowledgement: Hugo Rodger Brown (StackOverFlow) for this constructor notation: https://stackoverflow.com/questions/7274267/print-all-day-dates-between-two-dates
		date_range = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]

		# Import stock data in the desired date range
		df = get_historical_data(ticker, start=start_date, end=end_date, output_format='pandas')
		df.index.name = 'date'
		df.reset_index(inplace=True)

		capital = starting_capital
		num_shares = 0
		liquid = True
		
		previous_price = 0
		correct = [0, 0]

		for date in date_range:

			try:
				price = float(df.loc[df["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])
			except (KeyError, IndexError):
				continue

			if indicator(df, date, ticker, indicators_to_use[indicator]) == "SELL":
				if not liquid:
					sell_data = sell(liquid, date, ticker, capital, num_shares, price, previous_price, correct)
					liquid = sell_data[0]
					capital = sell_data[1]
					num_shares = sell_data[2]
					previous_price = sell_data[3]

			elif indicator(df, date, ticker, indicators_to_use[indicator]) == "BUY":
				if liquid:
					buy_data = buy(liquid, date, ticker, capital, num_shares, price, previous_price, correct)
					liquid = buy_data[0]
					capital = buy_data[1]
					num_shares = buy_data[2]
					previous_price = buy_data[3]

		if capital == 0:
			# Sell the remaining shares using the final date's price
			try:
				end_price = float(df.loc[df["date"] == end_date.strftime("%Y-%m-%d")][price_type].iloc[0])
			except (KeyError, IndexError):
			# If the exact end date is not in our database, print an error message, and set end_date to be the previous date
			# that appears in the database.
				new_end_date = max(date for date in df["date"] if date < end_date.strftime("%Y-%m-%d"))
				print("Your selected end date was not found in the database. Ending on " + new_end_date + " instead of " + end_date.strftime("%Y-%m-%d") + ".")
				end_price = float(df.loc[df["date"] == new_end_date][price_type].iloc[0])

			capital = num_shares * end_price
			num_shares = 0

		cprint("Finished with " + str(round(capital, 2)) + " dollars.", color='cyan')
		cprint("Made money in " + str(correct[0]) + " out of " + str(round(correct[1], 2)) + " decisions. Accuracy: " + str(float(correct[0])/correct[1]), color='cyan')


if __name__ == "__main__":

	# Launch interface: allows the user to either select a default date range 
	# and simulator, or specify their own.

	ticker = input("Ticker: ")
	defaults = input("Run with default settings? (y/n): ")
	while not defaults.lower() in ["y", "n"]:
		print("You did not enter a valid response.")
		defaults = input("Run with default settings? (y/n): ")

	if defaults.lower() == "y":
		#single_equity_simulator(1000, ticker, datetime(2015, 1, 25), datetime(2018, 8, 1))
		multiple_equity_simulator(1000, 7, datetime(2015, 1, 25), datetime(2015, 6, 2))


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


