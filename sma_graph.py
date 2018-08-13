
from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
from termcolor import colored, cprint

# Import algorithms
from simple_sma import simple_sma_trade
from buy_and_hold import buy_and_hold
from stochastic_oscillator import stochastic_oscillator

if __name__ == "__main__":

	simple_sma_trade(1000, 30, 90, "SVU", datetime(2015, 1, 25), datetime(2018, 8, 1))
	buy_and_hold(1000, "SVU", datetime(2015, 1, 25), datetime(2018, 8, 1))
	stochastic_oscillator(1000, "SVU", datetime(2015, 1, 25), datetime(2018, 8, 1), 14)

