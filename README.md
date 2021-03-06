# Trading-Algorithms

This repository represents the current state of an ambitious project on my part to implement and simulate a version of every major stock trading indicator used today.

Currently supported indicators:

* Buy and hold (not really an indicator, but a control against which others can be measured).
* Simple Moving Averages
* Price Crossover Moving Average
* Bollinger Bands
* Money Flow Index
* Relative Strength Index
* Stochastic Oscillator

If there's an indicator which is not yet implemented that you would like me to include, don't hesitate to get in touch or open an issue!

## Getting Started
Welcome to the project! Thank you for stopping by.

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
The code in this repository requires Python 3.4 or later. If you are running an older version of Python, [download the latest version here](https://www.python.org/downloads/).

The following installation instructions assume a familiarity running commands in a Terminal. __If you are unfamiliar with running commands on a terminal, there are two conventions to keep in mind__ when following the below instructions: (1) The ```$``` sign is a convention indicating that the following command is a command to be run in Terminal; do not include it when actually running your commands. (2) Square brackets are used to indicate variable information that you should include without the square brackets. For example, if a command says, `$ cd [project_folder]`, the real command would look something like `$ cd Trading-Algorithms` depending on the name of the project folder and your current location in your computer's file tree.

### Installation

1. Download the git repository to your computer:
```
$ git clone [project_url]
```

2. Edit the trading simulator file with the parameters you wish to simulate, then run one of the trading simulators. 
```
$ python3 trading_simulator_single.py
```
or 
```
$ python3 trading_simulator_multiple.py
```

The file `trading_simulator_single.py` allows the user to specify the indicators they would like to run, then compares performance between those indicators on a user-specified equity over a period of time. The file `trading_simulator_multiple.py` allows the user to specify a portfolio of equities to trade between, and then uses a trading strategy based on majority rule amongst a set of indicators to balance capital between equities in the portfolio.


## Deployment


## Built With

* [IEX Developer Platform (API)](https://iextrading.com/developer/)

## Contributing

If you wish to contribute to this project, we would welcome your support!

To offer feedback and ideas, please open an issue in the GitHub repository, or send me an email. 

## Authors

Current active developers: 

* [Michael Cooper](https://github.com/cooper-mj)

## License

## Acknowledgments

