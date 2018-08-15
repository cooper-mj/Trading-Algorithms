
from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

# Import algorithms
from simple_sma import simple_sma_trade
from buy_and_hold import buy_and_hold
from stochastic_oscillator import stochastic_oscillator
from price_crossover import sma_price_crossover
from relative_strength_index import rsi

if __name__ == "__main__":

	ticker = input("Ticker: ")
	defaults = input("Run with default settings? (y/n): ")
	while not defaults.lower() in ["y", "n"]:
		print("You did not enter a valid response.")
		defaults = input("Run with default settings? (y/n): ")

	if defaults.lower() == "y":
		rsi(1000, 30, 70, 30, ticker, datetime(2015, 1, 25), datetime(2018, 8, 1))

		# simple_sma_trade(1000, 30, 90, ticker, datetime(2015, 1, 25), datetime(2018, 8, 1))
		# sma_price_crossover(1000, 30, ticker, datetime(2015, 1, 25), datetime(2018, 8, 1))
		buy_and_hold(1000, ticker, datetime(2015, 1, 25), datetime(2018, 8, 1))
		# stochastic_oscillator(1000, ticker, datetime(2015, 1, 25), datetime(2018, 8, 1), 14)

	elif defaults.lower() == "n":
		user_input = []
		print("Please enter syntactically valid Python code on the following lines, to call the relevant trading algorithms with your desired parameters.")
		command = input("")
		user_input.append(command)
		while not command == "":
			command = input("")
			user_input.append(command)

		for command in user_input:
			exec(command)


