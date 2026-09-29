import numpy as np

from scipy.stats import norm


def bs_price(F, K, T, r, sigma, is_call = True):
    """F means Forward Price, K means Strike, T means time to expiry in years, 
    r means continously compounded risk-free-rate and sigma means volatility as a decimal NOT 
    percentage."""

    d1 = (np.log(F/K) + (sigma**2)*T/2) / (sigma*np.sqrt(T))

    d2 = d1 - sigma*np.sqrt(T)

    if is_call:
        price = np.exp(-r*T)*(F*norm.cdf(d1) - K*norm.cdf(d2))
    else:
        price = np.exp(-r*T)*(K*norm.cdf(-d2) - F*norm.cdf(-d1))

    return price

def bs_vega(F, K, T, r, sigma):
    """Sensitivity of the option price to changes in volatility. It is the same for calls and puts. It's always positive."""

    d1 = (np.log(F/K) + (sigma**2)*T/2) / (sigma*np.sqrt(T))

    vega = (np.exp(-r*T))*F*(norm.pdf(d1))*(np.sqrt(T))

    return vega