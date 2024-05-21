import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use("MacOSX")
import cvxpy as cp
import dataframe_image as dfi


class frontier:
    def __init__(self, returns):
        # accessing given data from main and assigning it so it can be used throughout class
        self.returns = returns.dropna()
        # annualising returns
        self.annualised_ror = self.returns.mean()*252
        self.cov_mat = self.returns.cov()*252
        # for later use
        self.symbols = self.returns.columns.values
        self.n_assets = len(self.symbols)
        np.set_printoptions(suppress=True, precision=5)

    def eff_front(self):

        avg_returns = self.annualised_ror.values
        cov_mat = self.cov_mat.values

        # creating the variable for the weights which will be changed by the solver to get the optimised results
        weights = cp.Variable(self.n_assets)
        gamma = cp.Parameter(nonneg=True)
        # creating the dataframes which will be changed as the weights are changed in the solver
        # quadform uses the equation (w^T) * y*w
        portf_rtn_cvx = avg_returns @ weights
        portf_vol_cvx = cp.quad_form(weights, cov_mat)

        # setting up the maximisation objective and using the solver to achieve this
        objective_function = cp.Maximize(portf_rtn_cvx - (gamma * portf_vol_cvx))
        problem = cp.Problem(objective_function,
                             [cp.sum(weights) == 1, weights >= 0])

        # setting the number of levels of risk
        N_POINTS = 25
        portf_rtn_cvx_ef = np.zeros(N_POINTS)
        portf_vol_cvx_ef = np.zeros(N_POINTS)
        # gamma_range: log is used for spacing of the gamma values to create a curved efficient frontier curve
        gamma_range = np.logspace(-3, 3, num=N_POINTS)


        # solving the problem for every level of investor risk level
        weights_ef = []
        for i in range(N_POINTS):
            gamma.value = gamma_range[i]
            problem.solve()
            portf_vol_cvx_ef[i] = cp.sqrt(portf_vol_cvx).value
            portf_rtn_cvx_ef[i] = portf_rtn_cvx.value
            weights_ef.append(weights.value)

        # creating a dataframe and array for the weights from the results
        weights_df = pd.DataFrame(weights_ef,
                                  columns=self.symbols,
                                  index=np.round(gamma_range, 3))
        weights = weights_df.to_numpy()

        # calculating each of the portfolios' returns
        portf_rtns = np.dot(weights, avg_returns)

        # calculating the portfolios' volatilities
        # for each list of weights (25) this is doing the portfolio volatility equation for each stock (468)
        # cannot be done in one go because weights shape has 25 so either tran or not one way is wrong shape
        portf_vol = []
        for i in range(0, len(weights)):
            portf_vol.append(np.sqrt(np.dot(weights[i].T,
                                            np.dot(cov_mat, weights[i]))))
        portf_vol = np.array(portf_vol)

        # getting all the portfolios' sharpe_ratio
        portf_sharpe_ratio = portf_rtns / portf_vol

        # creating a dataframe with the information
        portf_results_df = pd.DataFrame({'Returns': portf_rtns,
                                         'Volatility': portf_vol,
                                         'Sharpe_Ratio':
                                             portf_sharpe_ratio})


        # formatting the weights for the box plot so that it is more visually accessible
        tran_weights = weights_df.transpose()
        t_weights_dict = tran_weights.to_dict()
        positives_list = []

        # significance level to see if a stock's weights will be assigned to "other" category
        insig_level = 0.062
        for risk_level in weights_df.index:
            t_weights_dict[risk_level]["Other"] = 0
            for stock in tran_weights.index:
                if t_weights_dict[risk_level][stock] < insig_level:
                    t_weights_dict[risk_level]["Other"] = t_weights_dict[risk_level]["Other"] + t_weights_dict[risk_level][stock]
                    t_weights_dict[risk_level][stock] = 0
                elif t_weights_dict[risk_level][stock] >= insig_level:
                    positives_list.append(stock)
        positives_list = list(dict.fromkeys(positives_list))
        positives_list.append("Other")
        # creating a dataframe with the new, formatted, weights
        new_weights = pd.DataFrame(t_weights_dict)
        new_weights = new_weights.transpose()
        weights_box_plot = new_weights[new_weights.columns.intersection(positives_list)]

        # creating a box plot for the weightings for each risk level
        ax1 = weights_box_plot.plot(kind='bar', stacked=True, cmap='tab20')
        ax1.set(title='Weights allocation per risk-aversion level',
               xlabel=r'$\gamma$',
               ylabel='weight')
        plt.legend(bbox_to_anchor=(1, 1))

        # plotting the efficient frontier line for the portfolios and scatter points for the individual stocks
        fig2, ax2 = plt.subplots()
        ax2.plot(portf_vol_cvx_ef, portf_rtn_cvx_ef, 'g-')
        for asset_index in range(self.n_assets):
            plt.scatter(x=np.sqrt(cov_mat[asset_index, asset_index]),
                        y=avg_returns[asset_index],
                        label=self.symbols[asset_index],
                        s=50)

        ax2.set(title='Efficient Frontier',
               xlabel='Volatility',
               ylabel='Expected Returns', )

        # adding Gamma as the index for the table
        portf_results_df.insert(0, "Gamma", weights_box_plot.index)

        # finding the results to highlight (maximum Sharpe ratio and minimum volatility)
        max_sharpe_ind = np.argmax(portf_results_df.Sharpe_Ratio)
        max_sharpe_portf = portf_results_df.loc[max_sharpe_ind]
        min_vol_ind = np.argmin(portf_results_df.Volatility)
        min_vol_portf = portf_results_df.loc[min_vol_ind]
        # creatiing a dataframe from these highlights
        highlight_df = pd.concat([max_sharpe_portf, min_vol_portf], axis=1)
        new_header = ["Max Sharpe Ratio", "Minimum Volatilty"]
        highlight_df.columns = new_header


        # formatting the df to be exported
        portf_results_df = portf_results_df.style.set_properties(**{"text-align": "left"})
        portf_results_df.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])

        highlight_df = highlight_df.style.set_properties(**{"text-align": "left"})
        highlight_df.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])

        # exporting the df as an image
        dfi.export(portf_results_df, 'portfolio_results.png')
        dfi.export(highlight_df, 'highlight_results.png', )

        # collecting the weights to be used for the next period
        self.max_sharpe_portf_weights = weights_df.iloc[max_sharpe_portf.name]
        self.min_vol_portf_weights = weights_df.iloc[min_vol_portf.name]

    # returning the weights to be used for next period
    def weights(self):
        return self.max_sharpe_portf_weights, self.min_vol_portf_weights







