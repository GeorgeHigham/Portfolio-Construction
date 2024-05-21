import pandas as pd

class prices:
    def __init__(self):
        self.start_date = "2010-01-04"
        self.end_date = "2014-12-31"
        self.start_date_next = "2015-01-02"
        self.end_date_next = "2016-12-30"
        self.prices_data = pd.read_csv("data/prices-split-adjusted.csv")


    # converting into a dataframe for using closing price only
    # also removing any NaN (blank) values to ensure full data
    def format(self):
        # get the selected time period 2010-2014
        self.mask = (self.prices_data["date"] > self.start_date) & (
                self.prices_data["date"] <= self.end_date)
        self.prices_data = self.prices_data.loc[self.mask]
        # create table with correct formatting
        self.prices_df = self.prices_data.pivot(index="date", columns="symbol",
                                      values="close").dropna(axis=1, how="any")
        # return the companies in dataframe
        return self.prices_df.columns

    def stock_prices(self, companies):
        self.prices_df = self.prices_df[companies]
        return self.prices_df

    def stock_returns(self):
        self.returns_df = self.prices_df.pct_change()
        return self.returns_df

    # same as above for the next time period
    def format_next_period(self):
        self.mask_next = (self.prices_data["date"] > self.start_date_next) & (
                self.prices_data["date"] <= self.end_date_next)
        self.prices_data_next = self.prices_data.loc[self.mask_next]
        self.prices_df_next = self.prices_data_next.pivot(index="date", columns="symbol",
                                                values="close").dropna(axis=1, how="any")
        return self.prices_df.columns

    def stock_prices_next_period(self, companies):
        self.prices_df_next = self.prices_df_next[companies]
        return self.prices_df

    def stock_returns_next_period(self):
        self.returns_df = self.prices_df.pct_change()
        return self.returns_df










