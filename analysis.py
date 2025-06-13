from scipy.optimize import curve_fit
import numpy as np

x = np.linspace(1, 5, 5) + np.random.randn(5)
y = 2 * x

def lin(x, a, b):
    return a * x + b

popt, _ = curve_fit(lin, x, y, p0=[2, 0])
print(popt)
