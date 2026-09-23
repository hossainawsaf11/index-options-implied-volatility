import numpy as np

from scipy.stats import norm


def bs_price(F, K, T, r, sigma, is_call = True):
    """F means Forward Price, K means Strike, T means time to expiry in years, 
    r means continously compounded risk-free-rate and sigma means volatility as a decimaly NOT 
    percentage."""

    d1 = (np.log(F/K) + (sigma**2)*T/2) / (sigma*np.sqrt(T))

    d2 = d1 - sigma*np.sqrt(T)

    if is_call:
        price = np.exp(-r*T)*(F*norm.cdf(d1) - K*norm.cdf(d2))
    else:
        price = np.exp(-r*T)*(K*norm.cdf(-d2) - F*norm.cdf(-d1))

    return price

# tests i ran

# running a Put-call parity: C - P should equal the discounted (F - K)
F, K, T, r, sigma = 90, 100, 1, 0.04, 0.20
call = bs_price(F, K, T, r, sigma, True)
put = bs_price(F, K, T, r, sigma, False)
parity_lhs = call - put
parity_rhs = np.exp(-r*T)*(F-K)
print("Parity:", parity_lhs, parity_rhs, np.isclose(parity_lhs, parity_rhs))

# price is increasing in volatility
F, K, T, r = 90, 100, 1, 0.04
print("Vol 0.10:", bs_price(F, K, T, r, 0.10, True))
print("Vol 0.20:", bs_price(F, K, T, r, 0.20, True))
print("Vol 0.40:", bs_price(F, K, T, r, 0.40, True))

# as T approaches zero, price collapses to the payoff
F, K, T, r, sigma = 110, 100, 0.00001, 0.04, 0.20
print("Call at expiry:", bs_price(F, K, T, r, sigma, True), "expect ~10")
print("Put at expiry:", bs_price(F, K, T, r, sigma, False), "expect ~0")

def bs_vega(F, K, T, r, sigma):
    """Senisitivity of the option price to changes in volatility. It is the same for calls and puts. It's always positive."""

    d1 = (np.log(F/K) + (sigma**2)*T/2) / (sigma*np.sqrt(T))

    vega = (np.exp(-r*T))*F*(norm.pdf(d1))*(np.sqrt(T))

    return vega

#Test
F = 100
K = 100
T = 1
r = 0.04
sigma = 0.2
h = 0.0001

vega_analytic = bs_vega(F, K, T, r, sigma)

price_up = bs_price(F, K, T, r, sigma + h, is_call=True)

price_down = bs_price(F, K, T, r, sigma - h, is_call=True)

vega_numeric = (price_up-price_down)/(2*h)

print("Vega analytic:", vega_analytic)
print("Vega numeric:", vega_numeric)
print("Vega Match:", np.isclose(vega_analytic, vega_numeric, rtol=1e-4))