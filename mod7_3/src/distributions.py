from math import sqrt, pi, exp, erf, factorial

def UniformDensityFunc(x: float, a: float, b: float) -> float:
    return 0 if x < a or x > b else 1 / (b - a)


def UniformDistributionFunc(x: float, a: float, b: float) -> float:
    if x < a: return 0
    if x > b: return 1
    return (x - a) / (b - a)


def NormalDensityFunc(x: float, m: float, sigma: float) -> float:
    return (1 / sqrt(2 * pi) / sigma * exp(- ((x - m) / sigma) ** 2 / 2)
            if sigma > 0 else -1)


def NormalDistributionFunc(x: float, m: float, sigma: float) -> float:
    return ((1 + erf((x - m) / sigma / sqrt(2))) / 2
            if sigma > 0 else -1)

def ExponentialDensityFunc(x: float, lambda_param: float) -> float:
    return lambda_param * exp(-lambda_param * x) if x >= 0 else 0

def ExponentialDistributionFunc(x: float, lambda_param: float) -> float:
    return 1 - exp(-lambda_param * x) if x >= 0 else 0

def PoissonProbabilityFunc(k: int, lambda_param: float) -> float:
    return (lambda_param ** k * exp(-lambda_param)) / factorial(k)

def ErlangDensityFunc(x: float, k: int, lambda_param: float) -> float:
    if x < 0:
        return 0
    return (lambda_param ** k * x ** (k - 1) * exp(-lambda_param * x)) / factorial(k - 1)

def ErlangDistributionFunc(x: float, k: int, lambda_param: float) -> float:
    if x < 0:
        return 0
    return 1 - sum([(lambda_param * x) ** n * exp(-lambda_param * x) / factorial(n) for n in range(k)])