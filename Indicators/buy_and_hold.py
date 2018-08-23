
'''
Simulates a buy and hold trading strategy on a single equity.
Given that the single_equity_simulator checks whether or not
the portfolio is liquid before issuing a buy signal, it is sufficient
for the buy_and_hold strategy to simply issue a "BUY" signal. Then,
the equity will be purchased on the first date of the time period,
no more equity will be purchased in the interim (since the portfolio)
is not liquid), and the portfolio will be liquidated on the final
date of the time period.
'''
def buy_and_hold(df, date, ticker, unique_properties, price_type='close'):
	return "BUY"