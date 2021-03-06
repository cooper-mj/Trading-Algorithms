from termcolor import colored, cprint
from datetime import datetime

'''
Simulates the complete liquidation of a single-equity portfolio. This function
computes how much capital the equity could be sold for, prints a message indicating
that the equity has been sold, and updates the liquid (whether the portfolio consists
of cash or equities), capital, num_shares, and previous_price (a variable used for checking
how many of the trend predictions used by the indicator ended up being accurate) variables
accordingly. It returns these values as a tuple so that the caller function may make use of
them after this function has modified them.
'''
def sell(liquid, date, ticker, capital, num_shares, price, previous_price, correct):

	liquid = True
	capital = num_shares * price
	sell_msg = colored("Selling " + str(round(num_shares, 2)) + " shares of " + ticker + " at " + str(round(price, 2)) + " for " + str(round(capital, 2)), 'red')
	print(date.strftime("%Y-%m-%d") + " : " + sell_msg)
	num_shares = 0

	# Check to see if our last decision was the right one
	if price > previous_price:
		# Check if current price is less than price we bought for since
		# our last call was a buy - check if we made money
		correct[0] += 1
		correct[1] += 1
	else:
		correct[1] += 1
	previous_price = price

	return (liquid, capital, num_shares, previous_price)

'''
Simulates the purchase of a single-equity portfolio. This function computes
how many shares the capital in the portfolio could be exchanged for, then
updates the the liquid, capital, num_shares, and previous_price variables
accordingly. It returns these values as a tuple so that the caller function may make use of
them after this function has modified them.
'''
def buy(liquid, date, ticker, capital, num_shares, price, previous_price, correct):

	liquid = False
	num_shares = float(capital) / price
	buy_msg = colored("Buying " + str(round(num_shares, 2)) + " shares of " + ticker + " at " + str(round(price, 2)) + " for " + str(round(capital, 2)), 'green')
	print(date.strftime("%Y-%m-%d") + " : " + buy_msg)
	capital = 0

	# Check to see if our last decision was the right one
	if price < previous_price:
		# Check if current price is less than price we bought for since
		# our last call was a buy - check if we made money
		correct[0] += 1
		correct[1] += 1
	else:
		correct[1] += 1
	previous_price = price

	return (liquid, capital, num_shares, previous_price)
