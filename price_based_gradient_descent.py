from iexfinance import get_historical_data
from datetime import datetime
from datetime import timedelta
import numpy as np

def F(w):
	return sum((x.dot(w) - y)**2 for x, y in dataset) / len(dataset)

def dF(w):
	return sum( 2 * (x.dot(w) - y) * x for x, y in dataset) / len(dataset)

def price_based_gradient_descent(F, dF, d):
	w = np.zeros(d)
	eta = 0.001 # Step size
	for t in range(1, 500): # Take 500 steps
		value = F(w)
		gradient = dF(w)
		w = w - (eta/t) * gradient # Take one step
		print("Iteration {}, w = {}, F(w) = {}, F\'(w) = {}".format(t, w, value, gradient))

ticker = input("Enter ticker: ")
start_date = datetime(2015, 1, 1)
end_date = datetime(2018, 10, 1)
price_type = 'close'
interval = int(input("Enter an interval for pricing within the dataset: "))

# Generate dataset to train on
df = get_historical_data(ticker, start=start_date, end=end_date, output_format='pandas')
df.index.name = 'date'
df.reset_index(inplace=True)
date_range = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]

price_vals = df[price_type].values
print(price_vals)

dataset = []

for i in range(11 * interval, len(price_vals[11 * interval:])):
	x = price_vals[i-(11*interval): i-interval: interval]
	y = price_vals[i]
	print((x, y))
	dataset.append((x, y))
		
# Build dataset: x = 10-vector of prices from the previous 10 prices, spaced 30-days apart; y = price on current day.
print(df)
print(dataset)
price_based_gradient_descent(F, dF, 10)