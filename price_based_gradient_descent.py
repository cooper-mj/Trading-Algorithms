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
	eta = 0.0001 # Step size
	for t in range(500): # Take 500 steps
		value = F(w)
		gradient = dF(w)
		w = w - eta * gradient # Take one step
		print("Iteration {}, w = {}, F(w) = {}, F\'(w) = {}".format(t, w, value, gradient))

ticker = input("Enter ticker: ")
start_date = datetime(2018, 1, 1)
end_date = datetime(2018, 10, 1)
price_type = 'close'

df = get_historical_data(ticker, start=start_date, end=end_date, output_format='pandas')
df.index.name = 'date'
df.reset_index(inplace=True)
date_range = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]

price_vals = df[price_type].values
print(price_vals)

dataset = []

for i in range(11, len(price_vals[11:])):
	x = price_vals[i-11: i-1]
	y = price_vals[i]
	print((x, y))
	dataset.append((x, y))
		
# Build dataset: x = 10-vector of prices from the previous 10 days; y = price on current day.
print(df)
price_based_gradient_descent(F, dF, 10)