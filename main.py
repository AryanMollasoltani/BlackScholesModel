import numpy as np
from scipy.stats import norm

#np.set_printoptions(legacy = '1.25')
class BlackScholesModel:

    def __init__(self, S, K, sigma, r, t):
        self.S = S # S: Underlying price (The current price of a stock)
        self.K = K # K: Strike price (The price of the "option to buy the stock" at the time of expiration)
        self.sigma = sigma # \sigma: volatility (standard deviation of the stock)
        self.r = r # r: interest rate
        self.t = t # t: Time to expiration (In years)

        self.d_1 = (np.log(self.S/self.K)+(self.r+1/2*self.sigma**2)*self.t)/(self.sigma*np.sqrt(self.t))
        self.d_2 = self.d_1 - (self.sigma*np.sqrt(self.t))

        self.c_p = self.S * norm.cdf(self.d_1) - self.K * np.exp(-self.r * self.t) * norm.cdf(self.d_2)
        self.p_p = self.K*np.exp(-self.r*self.t)*norm.cdf(-self.d_2)-self.S*norm.cdf(-self.d_1)

    def call_price(self):
        return self.c_p

    def breakeven_call(self):
        return self.K + self.c_p # break-even cost for the call(total cost to bet the stock will rise over K)

    def put_price(self):
        return self.p_p

    def breakeven_put(self):
        return self.K - self.p_p # break-even cost for the put(total cost to bet the stock will fall under K)

    def put_call_parity(self):
        return self.c_p - self.p_p

    def int_value(self):
        return np.maximum(self.S-self.K, 0) # if int_val >  0, then the stock is ITM(in the money)

    def time_value(self):
        return self.c_p - np.maximum(self.S-self.K, 0)

    def gbm_path(self, n_steps, mu=None):
        # if nu is not given, use the theoretical value of r
        if mu is None:
            mu = self.r
        # this is the associated geometric brownian motion path of the price given the model parameters
        # mu stands for the drift coefficient, n is number of time steps, dt is the time step
        dt = self.t / n_steps
        time_values = np.linspace(0, self.t, n_steps + 1)

        # Brownian motion increments and compute cumulative sum
        dW = np.random.normal(0, np.sqrt(dt), size=n_steps)
        W = np.cumsum(dW)  # Cumulative Brownian motion
        W = np.insert(W, 0, 0)  # Start at W(0) = 0

        # We use exact solution to the SDE(My first approach was Euler-Maruyama)
        exponent = (mu - 0.5 * self.sigma ** 2) * time_values + self.sigma * W
        price_path = self.S * np.exp(exponent)

        return time_values, price_path

    def cp_heatmap_val(self, size=10, min_sig=None, max_sig=None, min_s=None, max_s=None):
        if min_sig is None:
            min_sig = self.sigma - 1/2*self.sigma
        if max_sig is None:
            max_sig = self.sigma + 1/2*self.sigma
        if min_s is None:
            min_s = self.S - 1/5*self.S
        if max_s is None:
            max_s = self.S + 1/5*self.S
        # this part of code can be also done for other parameters to create other heatmaps
        s_vals = np.linspace(min_s, max_s, size)
        sig_vals = np.linspace(min_sig, max_sig, size)
        X, Y = np.meshgrid(s_vals, sig_vals)
        model = BlackScholesModel(X, self.K, Y, self.r, self.t)
        calls = model.call_price()
        puts = model.put_price()
        return X, Y, calls, puts

    def thetas(self):
        term_one = -((self.S*self.sigma*norm.pdf(self.d_1))/(2*np.sqrt(self.t)))
        theta_call = term_one-self.r*self.K*np.exp(-self.r*self.t)*norm.cdf(self.d_2)
        theta_put = term_one+self.r*self.K*np.exp(-self.r*self.t)*norm.cdf(-self.d_2)
        # Theta peaks for at-the-money (ATM) options. Deep ITM options behave like the stock (low theta).
        # Deep OTM options have little value left to lose.
        theta_c_daily = theta_call/365
        theta_p_daily = theta_put/365
        return theta_call, theta_put, theta_c_daily, theta_p_daily

    def sensitivity_analysis(self, parameter=None):
        # for every $1 increase in S, call price goes up this amount
        delta_call = norm.cdf(self.d_1)
        delta_put = norm.cdf(self.d_1) - 1
        # Sensitivity of Delta to Stock Price(If S moves by 1$, delta moves by this amount)
        gamma = (norm.pdf(self.d_1))/(self.S*self.sigma*np.sqrt(self.t))
        # Sensitivity to Volatility (for 1% increase in sigma, option price moves this amount)
        vega = self.S*np.sqrt(self.t)*norm.pdf(self.d_1)
        # Sensitivity to Interest Rates(amount of price change to 1% change in r)
        rho_call = self.K*self.t*np.exp(-self.r*self.t)*norm.cdf(self.d_2)
        rho_put = -self.K*self.t*np.exp(-self.r*self.t)*norm.cdf(-self.d_2)
        if parameter is None:
            an = [delta_call, delta_put, gamma, vega, rho_call, rho_put]
            return an
        elif parameter == 'd':
            return delta_call, delta_put
        elif parameter == 'g':
            return gamma
        elif parameter == 'v':
            return vega
        elif parameter == 'r':
            return rho_call, rho_put
        else:
            an_o = [delta_call, delta_put, gamma, vega, rho_call, rho_put]
            return an_o

    def summary(self, market_price_at_expiry): # maybe unnecessary
        statline_call = []
        statline_put = []
        model = BlackScholesModel(self.S, self.K, self.sigma, self.r, self.t)
        statline_call.append(model.breakeven_call()) # stock must rise above this to profit
        statline_call.append(model.c_p) # max loss of call option in currency
        profit_call = market_price_at_expiry - model.breakeven_call()
        statline_call.append(profit_call)
        statline_put.append(model.breakeven_put())  # stock must fall below this to profit(Max gain)
        statline_put.append(model.p_p)  # max loss of put option in currency
        profit_put = model.breakeven_put() - market_price_at_expiry
        statline_put.append(profit_put)
        return statline_call, statline_put

    def theo_call_pnl(self, market_price):
        model = BlackScholesModel(self.S, self.K, self.sigma, self.r, self.t)
        pnl = market_price - model.breakeven_call()
        return pnl

    def theo_put_pnl(self, market_price):
        model = BlackScholesModel(self.S, self.K, self.sigma, self.r, self.t)
        pnl = model.breakeven_put() - market_price
        return pnl

    def theo_pnl_chart(self, size=10, min_sig=None, max_sig=None, min_mp=None, max_mp=None):
        if min_sig is None:
            min_sig = self.sigma - 1/2*self.sigma
        if max_sig is None:
            max_sig = self.sigma + 1/2*self.sigma
        if min_mp is None:
            min_mp = self.S - 1/5*self.S
        if max_mp is None:
            max_mp = self.S + 1/5*self.S

        market_prices_at_expiry = np.linspace(min_mp, max_mp, size)
        sig_vals = np.linspace(min_sig, max_sig, size)
        X, Y = np.meshgrid(market_prices_at_expiry, sig_vals)
        model = BlackScholesModel(self.S, self.K, Y, self.r, self.t)
        call_pnl = model.theo_call_pnl(market_prices_at_expiry)
        put_pnl = model.theo_put_pnl(market_prices_at_expiry)
        return X, Y, call_pnl, put_pnl
        # Remember we don't actually buy the option if the pnl is negative but this is not highlighted in model.

    def call_trade_edge(self, market_maker_quote):
        return self.c_p - market_maker_quote # the mispricing

    def put_trade_edge(self, market_maker_quote): # not as important as call
        return market_maker_quote - self.p_p

    def theta_decay_graph(self):
        T = np.linspace(1/365, self.t, int(self.t*365))
        d_1 = (np.log(self.S/self.K)+(self.r+1/2*self.sigma**2)*T)/(self.sigma*np.sqrt(T))
        d_2 = d_1 - (self.sigma*np.sqrt(T))
        term_one = -((self.S * self.sigma * norm.pdf(d_1)) / (2 * np.sqrt(T)))
        theta_call = term_one - self.r * self.K * np.exp(-self.r * T) * norm.cdf(d_2)
        theta_put = term_one + self.r * self.K * np.exp(-self.r * T) * norm.cdf(-d_2)

        return T, theta_call, theta_put, theta_call/365, theta_put/365

    def c_pnl_edge_simul(self, premium, num_contract, number_trade, mu = None):
        # use premium or market maker quote, number of contracts bought minimises the trading fees
        total_pnls = []
        if mu is None:
            mu = self.r
        model = BlackScholesModel(self.S, self.K, self.sigma, self.r, self.t)
        for _ in range(number_trade):
            sim_val = model.gbm_path(1000, mu)[1][-1]
            profit = np.maximum(sim_val - self.K, 0)*num_contract - premium*num_contract
            # we use max, because if the stock price is below the strike price at the time of expiry, then we
            # are not going to use the option therefore the profit is 0, but we always pay the premium for option
            total_pnls.append(profit)
        mean = np.mean(total_pnls)
        equity_curve = np.cumsum(total_pnls)
        return total_pnls, mean, equity_curve
        # if mean is too low, check with the theoretical pnl chart which explain even though the market is on our
        # side we don't profit much(remember the model doesn't account for extra fess)

Model = BlackScholesModel(62, 60, 0.32, 0.04, 40/365)
print(Model.call_price())
print(Model.c_pnl_edge_simul(3.25, 100, 10000)[1])

#def gbm_path(self, n_steps, mu=None):
#    if mu is None:
#        mu = self.r
#    # this is the associated geometric brownian motion path of the price given the model parameters
#    # mu stands for the drift, n is number of time steps, dt is the time step
#    price_path = []
#   dt = self.t / n_steps
#    previous_price = self.S
#    time_values = np.linspace(0, self.t, n_steps + 1)
#    for _ in time_values:
#        ds = mu * previous_price * dt + self.sigma * previous_price * np.random.randn() * np.sqrt(dt)
#        previous_price += ds
#        price_path.append(previous_price)
#    return time_values, price_path