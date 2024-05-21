import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import dataframe_image as dfi


class next_period:
    def __init__(self, weights, returns):
        # separate the weights transferred into the function
        self.max_sharpe_weights = weights[0]
        self.min_vol_weights = weights[1]
        # assign the total returns for all stocks
        self.returns = returns.dropna()

    def check_portf_results(self):

        # create a dataframe to plot the portfolio's price changes on a graph
        self.max_sharpe_daily_returns_list = []
        self.max_sharpe_daily_returns = self.returns @ self.max_sharpe_weights
        max_sharpe_price = 100
        for day_return in list(self.max_sharpe_daily_returns.values):
            self.max_sharpe_daily_returns_list.append(max_sharpe_price)
            max_sharpe_price *= (1 + day_return)

        self.min_vol_daily_returns_list = []
        self.min_vol_daily_returns = self.returns @ self.min_vol_weights
        min_vol_price = 100
        for day_return in list(self.min_vol_daily_returns.values):
            self.min_vol_daily_returns_list.append(min_vol_price)
            min_vol_price *= (1 + day_return)

        self.market_daily_returns_list = []
        self.market_daily_returns = self.returns.mean(axis=1)
        market_price = 100
        for day_return in list(self.market_daily_returns.values):
            self.market_daily_returns_list.append(market_price)
            market_price *= (1 + day_return)

        data_dict = {"Maximum Sharpe Ratio": self.max_sharpe_daily_returns_list,
                     "Minimum Volatility": self.min_vol_daily_returns_list,
                     "Market": self.market_daily_returns_list}
        self.price_change_df = pd.DataFrame(data_dict, index=self.returns.index)

        # annualise the returns to give the average
        stocks_returns = self.returns.mean() * 252
        # get all the stocks annual returns
        market_annual_return = stocks_returns.mean()
        # find the annualised return for the highlights & market
        self.max_sharpe_portf_return = stocks_returns @ self.max_sharpe_weights
        self.min_vol_portf_return = stocks_returns @ self.min_vol_weights
        self.market_return = self.returns.mean(axis=1).mean() * 252
        # calculate annualised volatility
        self.max_sharpe_vol = (self.returns @ self.max_sharpe_weights).std() * 252 ** 0.5
        self.min_vol_vol = (self.returns @ self.min_vol_weights).std() * 252 ** 0.5
        self.market_vol = (self.returns.mean(axis=1)).std() * 252 ** 0.5
        # calculating sharpe ratio
        self.max_sharpe_sharpe = self.max_sharpe_portf_return/self.max_sharpe_vol
        self.min_vol_sharpe = self.min_vol_portf_return / self.min_vol_vol
        self.market_sharpe = self.market_return / self.market_vol

        self.results_data = {"Returns": [self.max_sharpe_portf_return, self.min_vol_portf_return, self.market_return],
                             "Volatility": [self.max_sharpe_vol, self.min_vol_vol, self.market_vol],
                             "Sharpe Ratio": [self.max_sharpe_sharpe, self.min_vol_sharpe, self.market_sharpe]}
        index = pd.Index(["Max Sharpe Ratio", "Minimum Volatility", "Market"])
        self.results_df = pd.DataFrame(self.results_data).set_index(index)
        self.results_df = self.results_df.style.set_properties(**{"text-align": "left"})
        dfi.export(self.results_df, 'final_results.png')

    def visualise_portf_prices(self):
        # set up the figure and plot size
        fig, ax = plt.subplots(figsize=(10, 8))
        # axes formatting
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=14)
        plt.xlabel("Date", fontsize=14)
        plt.ylabel("Price", fontsize=14)
        # dates formatting
        self.price_change_df.index = pd.to_datetime(self.price_change_df.index)

        date_form = mdates.DateFormatter("%Y-%m-%d")
        ax.xaxis.set_major_formatter(date_form)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.tick_params(axis="x", rotation=45)

        # smooth the data
        self.roll_df = self.price_change_df.rolling(window=30).mean()

        # plot the graphs
        plt.subplot()
        plt.title("Portfolio Price Changes")
        plt.xlabel("Time")
        plt.ylabel("Portfolio Price Base 100")
        plt.plot(self.roll_df.index, self.roll_df)
        plt.legend(["Maximum Sharpe Ratio", "Minimum Volatility", "Market"])

        # revealing all the graphs plotted across the classes
        plt.show()
