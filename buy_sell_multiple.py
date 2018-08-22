from datetime import datetime
from termcolor import colored, cprint

'''
Simulates the purchase of the most buyable equities from cash.
'''
def buy_from_cash(portfolio, capital, most_buyable_equities, equity_data, date, price_type):
	N = len(most_buyable_equities)
	to_spend = capital / float(N)
	for buy_equity in most_buyable_equities:
		try:
			equity_price = float(equity_data[buy_equity].loc[equity_data[buy_equity]["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])
		except IndexError:
			continue
		num_shares = round(to_spend / float(equity_price), 2)

		buy_msg = colored("Buying " + str(num_shares) + " of " + buy_equity + " at " + str(round(equity_price, 2)) + " for " + str(to_spend), 'green')
		print(date.strftime("%Y-%m-%d") + " : " + buy_msg)
		capital -= to_spend
		portfolio[buy_equity] += num_shares
	return capital

'''
Simulates the selling of one equity, and the redistribution of
that capital into the most buyable equities.
'''
def redistribute_from_equity(portfolio, equity, equity_data, most_buyable_equities, date, price_type):
	sell_price = float(equity_data[equity].loc[equity_data[equity]["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])

	N = len(most_buyable_equities)
	capital_gain = portfolio[equity] * sell_price

	to_spend = capital_gain / float(N)
	for buy_equity in most_buyable_equities:
		try:
			buy_price = float(equity_data[buy_equity].loc[equity_data[buy_equity]["date"] == date.strftime("%Y-%m-%d")][price_type].iloc[0])
		except IndexError:
			continue
		num_shares = round(to_spend / float(buy_price), 2)
		sell_msg = colored("Selling " + str(round(portfolio[equity] / float(N), 2)) + " shares of " + equity + " at " + str(round(sell_price, 2)) + " for " + str(round(to_spend, 2)), 'red')
		
		buy_msg = colored("Buying " + str(num_shares) + " shares of " + buy_equity + " at " + str(buy_price) + " for " + str(round(to_spend, 2)), 'green')
		print(date.strftime("%Y-%m-%d") + " : " + sell_msg + "; " + buy_msg)

		portfolio[buy_equity] += num_shares

	portfolio[equity] = 0

'''
Simulates selling the entire portfolio. Prints out the net amount of
capital at the end.
'''
def cash_out_portfolio(portfolio, date, equity_data, end_date, price_type, capital):
	for equity in portfolio.keys():
		try:
			end_price = float(equity_data[equity].loc[equity_data[equity]["date"] == end_date.strftime("%Y-%m-%d")][price_type].iloc[0])
		except (KeyError, IndexError):
		# If the exact end date is not in our database, print an error message, and set end_date to be the previous date
		# that appears in the database.
			new_end_date = max(date for date in equity_data[equity]["date"] if date < end_date.strftime("%Y-%m-%d"))
			print("Your selected end date was not found in the database. Ending on " + new_end_date + " instead of " + end_date.strftime("%Y-%m-%d") + ".")
			end_price = float(equity_data[equity].loc[equity_data[equity]["date"] == new_end_date][price_type].iloc[0])

		cprint("Selling " + str(round(portfolio[equity], 2)) + " shares of " + equity + " at " + str(round(end_price, 2)) + " for " + str(round(portfolio[equity] * end_price, 2)) + " dollars.", 'cyan')

		capital += portfolio[equity] * end_price
	cprint("Finished with " + str(capital) + " dollars.", 'cyan')



