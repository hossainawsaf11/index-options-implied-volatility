import numpy as np
from src.black_scholes import bs_price, bs_vega


def test_put_call_parity():
    F, K, T, r, sigma = 90, 100, 1, 0.04, 0.20
    call = bs_price(F, K, T, r, sigma, True)
    put = bs_price(F, K, T, r, sigma, False)
    assert np.isclose(call - put, np.exp(-r*T)*(F - K))

def test_monotonic_in_vol():
    F, K, T, r = 90, 100, 1, 0.04
    low = bs_price(F, K, T, r, 0.10, True)
    mid = bs_price(F, K, T, r, 0.20, True)
    high = bs_price(F, K, T, r, 0.40, True)
    assert low < mid < high


def test_converges_to_payoff():
    F, K, T, r, sigma = 110, 100, 0.00001, 0.04, 0.20
    call = bs_price(F, K, T, r, sigma, True)
    put = bs_price(F, K, T, r, sigma, False)
    assert np.isclose(call, 10, rtol=1e-4)
    assert np.isclose(put, 0, atol=1e-8)


def test_vega_matches_finite_difference():
    F, K, T, r, sigma = 100, 100, 1, 0.04, 0.20
    h = 1e-4
    analytic = bs_vega(F, K, T, r, sigma)
    up = bs_price(F, K, T, r, sigma + h, True)
    down = bs_price(F, K, T, r, sigma - h, True)
    numeric = (up - down) / (2 * h)
    assert np.isclose(analytic, numeric, rtol=1e-8)