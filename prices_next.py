import pandas as pd

class prices_next:
    def __init__(self):
        self.start_date_next = "2015-01-02"
        self.end_date_next = "2016-12-30"
        self.prices_data = pd.read_csv("data/prices-split-adjusted.csv")

        # converting into a dataframe for using closing price only
        # also removing any NaN (blank) values to ensure full data

    def format_next(self):
        # get the selected time period 2010-2014
        self.mask_next = (self.prices_data["date"] > self.start_date_next) & (
                self.prices_data["date"] <= self.end_date_next)
        self.prices_data_next = self.prices_data.loc[self.mask_next]
        # create table with correct formatting
        self.prices_df_next = self.prices_data_next.pivot(index="date", columns="symbol",
                                                values="close").dropna(axis=1, how="any")
        # return the companies in dataframe
        return self.prices_df_next.columns

    def stock_prices_next(self, companies):
        self.prices_df_next = self.prices_df_next[companies]
        return self.prices_df_next

    def stock_returns_next(self):
        self.returns_df_next = self.prices_df_next.pct_change()
        return self.returns_df_next












