from prices import prices
from efficient_frontier import frontier
from prices_next import prices_next
from next_period import next_period

# initialising class
prices = prices()
prices_next = prices_next()

# formatting data for these companies
# checking data is available for all companies
prices_company_list = prices.format()
prices_next_company_list = prices_next.format_next()

# intersect the companies from the two different time periods and use as company list
company_list = sorted((prices_company_list.intersection(prices_next_company_list)))

# pulling stock prices and returns from prices class
stock_prices = prices.stock_prices(company_list)
stock_returns = prices.stock_returns()

# creating the efficient frontier, and returning various other graphs and tables
frontier = frontier(stock_returns)
frontier.eff_front()
highlight_weights = list(frontier.weights())


# pulling stock prices and returns from prices class
stock_prices_next = prices_next.stock_prices_next(company_list)
stock_returns_next = prices_next.stock_returns_next()

# using the portfolio's I have created and seeing their returns for the next two years
next_period = next_period(highlight_weights, stock_returns_next)
next_period.check_portf_results()
next_period.visualise_portf_prices()


